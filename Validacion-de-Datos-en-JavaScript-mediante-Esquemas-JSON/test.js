const assert = require("assert");
const validate = require("./validadorGenerado");

// casos de prueba
const casos = [
  { nombre: "Ana", edad: 22, correo: "ana@gmail.com" },
  { nombre: "Jo", edad: 15, correo: "malcorreo" },
  { nombre: "Mateo", edad: 20, correo: "mateo@gmail.com" },
  { nombre: "Lu", edad: 25, correo: "lu@mail.com" },
  { nombre: "Maria", edad: 17, correo: "maria@hotmail.com" },
];

console.log("Probando validador...\n");

casos.forEach((c, i) => {
  const ok = validate(c);
  console.log("Caso", i + 1, ":", ok ? "valido" : "inválido");

  if (i === 0 || i === 2) {
    assert.strictEqual(ok, true);
  } else {
    assert.strictEqual(ok, false);
  }
});

console.log("\nTodas las pruebas pasaron!");
