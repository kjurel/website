from http.server import BaseHTTPRequestHandler

import pkg_resources


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        installed_packages = {pkg.key: pkg.extras for pkg in pkg_resources.working_set}
        installed_packages = {
            pkg.key: pkg.get_metadata("installed-files").split("\n")
            for pkg in pkg_resources.working_set
        }

        package_sizes = {
            package: sum(int(item.split(",")[2]) for item in files if item)
            for package, files in installed_packages.items()
        }

        self.wfile.write(
            f"Hello, world!\ninstalled_packages = {installed_packages}\npackage_sizes = {package_sizes}".encode(
                "utf-8"
            )
        )
        return
