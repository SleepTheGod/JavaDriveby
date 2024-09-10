import os
import subprocess
import shutil
import http.server
import socketserver

# Define paths
cpp_file = 'module.cpp'
wasm_file = 'module.wasm'
js_file = 'module.js'
html_file = 'index.html'
build_dir = 'build'

# C++ code to compile
cpp_code = '''\
#include <emscripten/emscripten.h>

extern "C" {

EMSCRIPTEN_KEEPALIVE
void executeOutSandbox() {
    printf("Executed outSandbox method in WebAssembly.\\n");
}

}
'''

# HTML content to serve
html_content = '''\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebAssembly Integration</title>
    <script>
        async function loadWasm() {
            try {
                const response = await fetch('module.wasm');
                const wasmArrayBuffer = await response.arrayBuffer();
                const { instance } = await WebAssembly.instantiate(wasmArrayBuffer);
                return instance.exports;
            } catch (error) {
                console.error('Failed to load WebAssembly module:', error);
                throw error;
            }
        }

        async function init() {
            try {
                const wasmExports = await loadWasm();
                // Assuming the function is named executeOutSandbox
                wasmExports.executeOutSandbox();
            } catch (error) {
                console.error('Initialization failed:', error);
            }
        }

        document.addEventListener('DOMContentLoaded', init);
    </script>
</head>
<body>
    <h1>WebAssembly Example</h1>
    <p>Check the console for WebAssembly output.</p>
</body>
</html>
'''

def main():
    # Create build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    # Write C++ code to file
    with open(os.path.join(build_dir, cpp_file), 'w') as f:
        f.write(cpp_code)

    # Compile C++ to WebAssembly using Emscripten
    try:
        subprocess.run([
            'emcc', os.path.join(build_dir, cpp_file),
            '-o', os.path.join(build_dir, js_file),
            '-s', 'EXPORTED_FUNCTIONS=["_executeOutSandbox"]',
            '-s', 'EXPORTED_RUNTIME_METHODS=["cwrap"]'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")
        return

    # Write HTML content to file
    with open(os.path.join(build_dir, html_file), 'w') as f:
        f.write(html_content)

    # Start HTTP server
    port = 8000
    os.chdir(build_dir)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == '__main__':
    main()
