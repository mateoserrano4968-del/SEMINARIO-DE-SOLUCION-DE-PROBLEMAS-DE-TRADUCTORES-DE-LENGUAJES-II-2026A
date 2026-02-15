
const Ajv = require("ajv");
const addFormats = require("ajv-formats");
const ajv = new Ajv();
addFormats(ajv);

const schema = {
  "type": "object",
  "properties": {
    "nombre": {
      "type": "string",
      "minLength": 3
    },
    "edad": {
      "type": "number",
      "minimum": 18
    },
    "correo": {
      "type": "string",
      "format": "email"
    }
  },
  "required": [
    "nombre",
    "edad",
    "correo"
  ]
};

const validate = ajv.compile(schema);

module.exports = validate;
