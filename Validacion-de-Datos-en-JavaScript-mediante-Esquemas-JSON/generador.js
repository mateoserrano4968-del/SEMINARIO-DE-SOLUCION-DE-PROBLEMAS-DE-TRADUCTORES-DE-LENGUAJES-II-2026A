const fs = require("fs");
const Ajv = require("ajv");
const addFormats = require("ajv-formats");

const schema = JSON.parse(fs.readFileSync("schema.json", "utf-8"));

function generarCodigoAjv(schema) {
  return `
const Ajv = require("ajv");
const addFormats = require("ajv-formats");
const ajv = new Ajv();
addFormats(ajv);

const schema = ${JSON.stringify(schema, null, 2)};

const validate = ajv.compile(schema);

module.exports = validate;
`;
}

const codigo = generarCodigoAjv(schema);

fs.writeFileSync("validadorGenerado.js", codigo);

console.log("Codigo generado:\n");
console.log(codigo);

const datos = JSON.parse(fs.readFileSync("datos.json", "utf-8"));

const ajv = new Ajv();
addFormats(ajv);
const validate = ajv.compile(schema);

if (validate(datos)) {
  console.log("\n✅ Datos válidos");
} else {
  console.log("\n❌ Errores:", validate.errors);
}
