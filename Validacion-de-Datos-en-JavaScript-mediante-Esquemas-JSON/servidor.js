const http = require("http");
const fs = require("fs");
const path = require("path");

const puerto = 3000;

const servidor = http.createServer((req, res) => {
  let ruta = req.url === "/" ? "/index.html" : req.url;
  const archivo = path.join(__dirname, ruta);

  fs.readFile(archivo, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end("no encontrado");
      return;
    }
    const ext = path.extname(archivo);
    const tipos = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json" };
    res.writeHead(200, { "Content-Type": tipos[ext] || "text/plain" });
    res.end(data);
  });
});

servidor.listen(puerto, () => {
  console.log("Servidor en http://localhost:" + puerto);
  console.log("Abre el navegador en esa direccion");
});
