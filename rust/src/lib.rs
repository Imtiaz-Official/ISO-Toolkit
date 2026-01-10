use pyo3::prelude::*;
use pyo3::types::PyDict;
use reqwest::Client;
use sha2::{Sha256, Digest};
use md5::Md5;
use std::fs::{File, OpenOptions};
use std::io::{self, Write, Read};
use std::path::Path;
use std::time::Duration;
use tokio::runtime::Runtime;
use serde::{Deserialize, Serialize};

/// File information structure
#[pyclass]
#[derive(Serialize, Deserialize, Clone)]
pub struct FileInfo {
    #[pyo3(get, set)]
    pub size: u64,
    #[pyo3(get, set)]
    pub supports_range: bool,
    #[pyo3(get, set)]
    pub content_type: String,
}

/// Download result structure
#[pyclass]
pub struct DownloadResult {
    #[pyo3(get, set)]
    pub success: bool,
    #[pyo3(get, set)]
    pub bytes_downloaded: u64,
    #[pyo3(get, set)]
    pub error_message: Option<String>,
}

/// Progress callback during download
type ProgressCallback = PyObject;

/// Get file information from URL without downloading
#[pyfunction]
fn get_file_info(url: &str) -> PyResult<FileInfo> {
    let rt = Runtime::new()?;
    let info = rt.block_on(async {
        let client = Client::builder()
            .timeout(Duration::from_secs(10))
            .build()?;

        let response = client.head(url).send().await?;

        Ok(FileInfo {
            size: response.content_length().unwrap_or(0),
            supports_range: response
                .headers()
                .get("accept-ranges")
                .and_then(|v| v.to_str().ok())
                .map(|v| v.eq_ignore_ascii_case("bytes"))
                .unwrap_or(false),
            content_type: response
                .headers()
                .get("content-type")
                .and_then(|v| v.to_str().ok())
                .unwrap_or("application/octet-stream")
                .to_string(),
        })
    })?;
    Ok(info)
}

/// Download a file with progress callback
#[pyfunction]
fn download_file(
    url: &str,
    output_path: &str,
    resume: bool,
    progress_callback: Option<ProgressCallback>,
    py: Python,
) -> PyResult<DownloadResult> {
    let rt = Runtime::new()?;
    let result = rt.block_on(async {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .build()?;

        let path = Path::new(output_path);
        let mut start_pos = 0u64;

        // Check for resume
        if resume && path.exists() {
            if let Ok(metadata) = path.metadata() {
                start_pos = metadata.len();
            }
        }

        // Build request with range header for resume
        let mut request = client.get(url);
        if start_pos > 0 {
            request = request.header("Range", format!("bytes={}-", start_pos));
        }

        let response = request.send().await?;

        if !response.status().is_success() && response.status().as_u16() != 206 {
            return Ok(DownloadResult {
                success: false,
                bytes_downloaded: 0,
                error_message: Some(format!("HTTP error: {}", response.status())),
            });
        }

        let total_size = response.content_length().unwrap_or(0) + start_pos;
        let mut file = if start_pos > 0 {
            OpenOptions::new().append(true).open(path)?
        } else {
            File::create(path)?
        };

        let mut downloaded = start_pos;
        let mut buffer = vec![0u8; 8192];
        let mut stream = response.bytes_stream();

        while let Some(chunk_result) = stream.next().await {
            let chunk = chunk_result?;

            file.write_all(&chunk)?;
            downloaded += chunk.len() as u64;

            // Call progress callback
            if let Some(ref callback) = progress_callback {
                let result = callback.call1(
                    py,
                    (downloaded, total_size),
                );
                if result.is_err() {
                    break; // User cancelled
                }
            }
        }

        Ok(DownloadResult {
            success: true,
            bytes_downloaded: downloaded,
            error_message: None,
        })
    })?;

    Ok(result)
}

/// Verify file checksum
#[pyfunction]
fn verify_checksum(file_path: &str, expected: &str, algorithm: &str) -> PyResult<bool> {
    let path = Path::new(file_path);

    let result = match algorithm.to_lowercase().as_str() {
        "sha256" => {
            let mut hasher = Sha256::new();
            let mut file = File::open(path)?;
            let mut buffer = vec![0u8; 8192];

            loop {
                let n = file.read(&mut buffer)?;
                if n == 0 {
                    break;
                }
                hasher.update(&buffer[..n]);
            }

            let result = hasher.finalize();
            let calculated = format!("{:x}", result);
            calculated.eq_ignore_ascii_case(expected)
        }
        "md5" => {
            let mut hasher = Md5::new();
            let mut file = File::open(path)?;
            let mut buffer = vec![0u8; 8192];

            loop {
                let n = file.read(&mut buffer)?;
                if n == 0 {
                    break;
                }
                hasher.update(&buffer[..n]);
            }

            let result = hasher.finalize();
            let calculated = format!("{:x}", result);
            calculated.eq_ignore_ascii_case(expected)
        }
        _ => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Unsupported algorithm: {}", algorithm)
        )),
    };

    Ok(result)
}

/// Format bytes to human readable format
#[pyfunction]
fn format_bytes(bytes: u64) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB", "TB"];
    let mut size = bytes as f64;
    let mut unit_index = 0;

    while size >= 1024.0 && unit_index < UNITS.len() - 1 {
        size /= 1024.0;
        unit_index += 1;
    }

    if unit_index == 0 {
        format!("{} {}", bytes, UNITS[unit_index])
    } else {
        format!("{:.1} {}", size, UNITS[unit_index])
    }
}

/// Format seconds to human readable duration
#[pyfunction]
fn format_duration(seconds: u64) -> String {
    if seconds < 60 {
        format!("{}s", seconds)
    } else if seconds < 3600 {
        let mins = seconds / 60;
        let secs = seconds % 60;
        format!("{}m {}s", mins, secs)
    } else {
        let hours = seconds / 3600;
        let mins = (seconds % 3600) / 60;
        format!("{}h {}m", hours, mins)
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FileInfo>()?;
    m.add_class::<DownloadResult>()?;
    m.add_function(wrap_pyfunction!(get_file_info, m)?)?;
    m.add_function(wrap_pyfunction!(download_file, m)?)?;
    m.add_function(wrap_pyfunction!(verify_checksum, m)?)?;
    m.add_function(wrap_pyfunction!(format_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(format_duration, m)?)?;
    Ok(())
}
