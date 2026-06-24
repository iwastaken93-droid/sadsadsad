#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            commands::analyze_code,
            commands::roast_code,
            commands::get_config,
            commands::save_config,
            commands::get_personas,
            commands::start_backend,
            commands::stop_backend,
            commands::check_backend,
        ])
        .run(tauri::generate_context!())
        .expect("error while running RoastMe");
}
