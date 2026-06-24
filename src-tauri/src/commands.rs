use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::State;

// ── Backend process management ──────────────────────────────

struct BackendState {
    process: Mutex<Option<Child>>,
}

#[tauri::command]
fn start_backend(state: State<BackendState>) -> Result<String, String> {
    let mut guard = state.process.lock().unwrap();
    if guard.is_some() {
        return Ok("already running".to_string());
    }
    let child = Command::new("roastme")
        .args(["serve", "--port", "8137"])
        .spawn()
        .map_err(|e| format!("Failed to start backend: {}", e))?;
    *guard = Some(child);
    Ok("started".to_string())
}

#[tauri::command]
fn stop_backend(state: State<BackendState>) -> Result<String, String> {
    let mut guard = state.process.lock().unwrap();
    if let Some(mut child) = guard.take() {
        child.kill().map_err(|e| format!("Failed to stop: {}", e))?;
        Ok("stopped".to_string())
    } else {
        Ok("not running".to_string())
    }
}

#[tauri::command]
fn check_backend() -> bool {
    // Quick check if backend is responding
    std::process::Command::new("curl")
        .args(["-s", "http://localhost:8137/api/personas"])
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

// ── Proxy commands (forward to Python backend) ──────────────

#[derive(Deserialize)]
struct AnalyzeRequest {
    source: String,
    file_path: String,
}

#[derive(Deserialize)]
struct RoastConfigReq {
    api_key: String,
    api_base: String,
    model: String,
    roast_level: String,
    persona: String,
}

#[derive(Deserialize)]
struct RoastRequest {
    source: String,
    file_path: String,
    config: RoastConfigReq,
}

#[tauri::command]
async fn analyze_code(req: AnalyzeRequest) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post("http://localhost:8137/api/analyze")
        .json(&req)
        .send()
        .await
        .map_err(|e| format!("Backend unreachable: {}", e))?;
    let json = resp.json::<serde_json::Value>().await
        .map_err(|e| format!("Parse error: {}", e))?;
    Ok(json)
}

#[tauri::command]
async fn roast_code(req: RoastRequest) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .post("http://localhost:8137/api/roast")
        .json(&req)
        .send()
        .await
        .map_err(|e| format!("Backend unreachable: {}", e))?;
    let json = resp.json::<serde_json::Value>().await
        .map_err(|e| format!("Parse error: {}", e))?;
    Ok(json)
}

#[tauri::command]
async fn get_config() -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .get("http://localhost:8137/api/config")
        .send()
        .await
        .map_err(|e| format!("Backend unreachable: {}", e))?;
    let json = resp.json::<serde_json::Value>().await
        .map_err(|e| format!("Parse error: {}", e))?;
    Ok(json)
}

#[tauri::command]
async fn save_config(req: RoastConfigReq) -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let mut map = HashMap::new();
    map.insert("api_key", req.api_key);
    map.insert("api_base", req.api_base);
    map.insert("model", req.model);
    map.insert("roast_level", req.roast_level);
    map.insert("persona", req.persona);
    
    let resp = client
        .post("http://localhost:8137/api/config")
        .json(&map)
        .send()
        .await
        .map_err(|e| format!("Backend unreachable: {}", e))?;
    let json = resp.json::<serde_json::Value>().await
        .map_err(|e| format!("Parse error: {}", e))?;
    Ok(json)
}

#[tauri::command]
async fn get_personas() -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let resp = client
        .get("http://localhost:8137/api/personas")
        .send()
        .await
        .map_err(|e| format!("Backend unreachable: {}", e))?;
    let json = resp.json::<serde_json::Value>().await
        .map_err(|e| format!("Parse error: {}", e))?;
    Ok(json)
}
