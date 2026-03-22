#ifndef _ARBOLSINTACTICO
#define _ARBOLSINTACTICO

#include <string>
#include <iostream>
#include "tablaSimbolos.h"

using namespace std;

class Nodo{
public:
	string simbolo;
	Nodo *sig;
	char tipoDato;
	static TablaSimbolos *tablaSimbolos;
	static string ambito;
	
	static int sangria;
	void muestraSangria(){
		for (int i=0; i < sangria; i++)
		cout << " ";
	}

	virtual void muestra() {};
	virtual void validaTipos() {
		tipoDato= 'v';
		if (sig != NULL) sig->validaTipos();
	}

};

class Tipo: public Nodo{
public:
	Tipo(string simbolo){
		this->simbolo= simbolo;
		this->sig=NULL;
	}

	void muestra(){
		muestraSangria();
		cout << "<Tipo> " << simbolo << endl;
	}

	char dimeTipo() {
		if (simbolo.compare("int") == 0) return 'i';
		if (simbolo.compare("float") == 0) return 'f';
		if (simbolo.compare("string") == 0) return 's';
		if (simbolo.compare("void") == 0) return 'v';
		return 'v';
	}

};

class Expresion: public Nodo{
public:
	Expresion *izq, *der;
		string guardaArbol(){
		return "";
	}

};

class Identificador: public Expresion{
public:
	Identificador(string simbolo, Nodo *sig=NULL){
		this->simbolo= simbolo;
		this->sig=sig;
	}

	void muestra(){
		muestraSangria();
		cout << "<Identificador> " << simbolo << endl;
		if (sig != NULL) sig->muestra();
	}

	void validaTipos(){
		tablaSimbolos->buscaIdentificador(simbolo);
		if (tablaSimbolos->varLocal != NULL) tipoDato= tablaSimbolos->varLocal->tipo;
		else if (tablaSimbolos->varGlobal != NULL) tipoDato= tablaSimbolos->varGlobal->tipo;
		else {
			tipoDato= 'v';
			tablaSimbolos->listaErrores->push_back("Error: variable \"" + simbolo + "\" no definida");
		}
		if (sig != NULL) sig->validaTipos();
	}

};

class DefVar: public Nodo{
public:
	Tipo *tipo;
	Identificador *listaVar;
	friend class TablaSimbolos;

	DefVar(Tipo *tipo, Identificador *listaVar, Nodo *sig){
		this->tipo= tipo;
		this->listaVar= listaVar;
		this->sig = sig;
	}

	void muestra(){
		muestraSangria();
		cout << "<DefVar> " << endl;
		
		Nodo::sangria++;
		tipo->muestra();
		listaVar->muestra();
		Nodo::sangria--;

		if (sig != NULL) sig->muestra();
	}

	void validaTipos(){
		tipoDato= tipo->dimeTipo();
		tablaSimbolos->agrega(this);
		if (sig != NULL) sig->validaTipos();
	}

};

class Parametro: public Nodo{
protected:
	Tipo *tipo;
	Identificador *id;
	friend class TablaSimbolos;

public:

	Parametro (Tipo *tipo, Identificador *id, Nodo *sig){
		this->tipo= tipo;
		this->id= id;
		this->sig= sig;
	}

	void muestra(){
		muestraSangria();
		cout << "<Parametro> " << endl;
		
		Nodo::sangria++;
		tipo->muestra();
		id->muestra();
		Nodo::sangria--;

		if (sig != NULL) sig->muestra();
	}

	string cadTipos(){
		string cad;
		cad += tipo->dimeTipo();
		Parametro *p= (Parametro*)sig;

		while (p != NULL){
			cad += p->tipo->dimeTipo();
			p= (Parametro*)p->sig;
		}

		return cad;
	}

	void validaTipos(){
		if (sig != NULL) sig->validaTipos();
	}

};



class DefFunc: public Nodo{
protected:
	Tipo *tipo;
	Identificador *id;
	Parametro *parametros;
	Nodo *bloqueFunc;
	friend class TablaSimbolos;

public:

	DefFunc(	Tipo *tipo, Identificador *id, Parametro *parametros, Nodo *bloqueFunc, Nodo *sig){
		this->tipo= tipo;
		this->id= id;
		this->parametros= parametros;
		this->bloqueFunc= bloqueFunc;
		this->sig= sig;
	}

	void muestra(){
		muestraSangria();
		cout << "<DefFunc> " << endl;
		
		Nodo::sangria++;
		tipo->muestra();
		id->muestra();
		if (parametros) parametros->muestra();
		if (bloqueFunc) bloqueFunc->muestra();
		Nodo::sangria--;

		if (sig != NULL) sig->muestra();
	}

	void validaTipos(){
		tablaSimbolos->agrega(this);
		string ambitoAnt= Nodo::ambito;
		Nodo::ambito= id->simbolo;
		if (parametros != NULL) tablaSimbolos->agrega(parametros);
		if (parametros != NULL) parametros->validaTipos();
		if (bloqueFunc != NULL) bloqueFunc->validaTipos();
		Nodo::ambito= ambitoAnt;
		if (sig != NULL) sig->validaTipos();
	}

};


class Asignacion: public Nodo{
public:
	Identificador *id;
	Expresion *expresion;
	friend class TablaSimbolos;

	Asignacion(	Identificador *id, Expresion *expresion, Nodo *sig= NULL){
		this->id= id;
		this->expresion= expresion;
		this->sig= sig;

	}

	void muestra(){
		muestraSangria();
		cout << "<Asignacion> " << endl;
		
		Nodo::sangria++;
		id->muestra();
		expresion->muestra();
		Nodo::sangria--;

		if (sig != NULL) sig->muestra();
	}

	void validaTipos(){
		if (id != NULL) id->validaTipos();
		if (expresion != NULL) expresion->validaTipos();
		if (id != NULL && expresion != NULL && id->tipoDato != expresion->tipoDato){
			tablaSimbolos->listaErrores->push_back("Error: tipos incompatibles en asignacion \"" + id->simbolo + "\"");
		}
		if (sig != NULL) sig->validaTipos();
	}

};

class Regresa: public Nodo{
protected:
	Expresion *expresion;
	friend class TablaSimbolos;

public:
	
	Regresa(Expresion *expresion, Nodo *sig= NULL){
		this->expresion= expresion;
		this->sig= sig;
	}

	void muestra(){
		muestraSangria();
		cout << "<Regresa> " << endl;
		
		Nodo::sangria++;		
			expresion->muestra();
		Nodo::sangria--;

		if (sig != NULL) sig->muestra();
	}

	void validaTipos(){
		if (expresion != NULL) expresion->validaTipos();
		if (sig != NULL) sig->validaTipos();
	}

};

class Entero: public Expresion{
public:
	Entero(string simbolo){
		this->simbolo= simbolo;
		this->sig=NULL;
	}

	void muestra(){
		muestraSangria();
		cout << "<Entero> " << simbolo << endl;
	}

	void validaTipos(){
		tipoDato= 'i';
		if (sig != NULL) sig->validaTipos();
	}
};

class Real: public Expresion{
public:
	Real(string simbolo){
		this->simbolo= simbolo;
		this->sig=NULL;
	}

	void muestra(){
		muestraSangria();
		cout << "<Real> " << simbolo << endl;
	}

	void validaTipos(){
		tipoDato= 'f';
		if (sig != NULL) sig->validaTipos();
	}
};

class Cadena: public Expresion{
public:
	Cadena(string simbolo){
		this->simbolo= simbolo;
		this->sig=NULL;
	}

	void muestra(){
		muestraSangria();
		cout << "<Cadena> " << simbolo << endl;
	}

	void validaTipos(){
		tipoDato= 's';
		if (sig != NULL) sig->validaTipos();
	}
};

class Signo: public Expresion{
protected:	
public:

	Signo(string simbolo, Expresion *izq){
		this->simbolo = simbolo;
		this->izq= izq;
		sig= NULL;
	}

	void muestra(){
		muestraSangria();
		cout << "<Signo> " << endl;
		
		Nodo::sangria++;		
			izq->muestra();
		Nodo::sangria--;

		if (sig != NULL) sig->muestra();
	}

	void validaTipos(){
		if (izq != NULL) izq->validaTipos();
		tipoDato= izq->tipoDato;
		if (sig != NULL) sig->validaTipos();
	}

};

class Mult: public Expresion{
protected:	
public:

	Mult(string simbolo, Expresion *izq, Expresion *der){
		this->der= der;
		this->simbolo= simbolo;
		this->izq= izq;
		sig= NULL;

	}

	void muestra(){
		muestraSangria();
		cout << "<Multiplicacion> " << simbolo << endl;
		
		Nodo::sangria++;		
			izq->muestra();
			der->muestra();
		Nodo::sangria--;

		if (sig != NULL) sig->muestra();
	}

	string guardaArbol(){
		return "new Mult(" + simbolo + "," + izq->guardaArbol() + ", " +  der->guardaArbol() + ") ";
	}

	void validaTipos(){
		if (izq != NULL) izq->validaTipos();
		if (der != NULL) der->validaTipos();
		if (izq->tipoDato == 'i' && der->tipoDato == 'i') tipoDato= 'i';
		else if (izq->tipoDato == 'f' || der->tipoDato == 'f') tipoDato= 'f';
		else tipoDato= 'v';
		if (sig != NULL) sig->validaTipos();
	}
};

class Suma: public Expresion{
protected:	
public:

	Suma(string simbolo, Expresion *izq, Expresion *der){
		this->der= der;
		this->simbolo= simbolo;
		this->izq= izq;
		sig= NULL;

	}

	void muestra(){
		muestraSangria();
		cout << "<Suma> " << simbolo << endl;
		
		Nodo::sangria++;		
			izq->muestra();
			der->muestra();
		Nodo::sangria--;

		if (sig != NULL) sig->muestra();
	}


	string guardaArbol(){
		return "new Suma(" + simbolo + "," + izq->guardaArbol() + ", " +  der->guardaArbol() + ") ";
	}

	void validaTipos(){
		if (izq != NULL) izq->validaTipos();
		if (der != NULL) der->validaTipos();
		if (izq->tipoDato == 'i' && der->tipoDato == 'i') tipoDato= 'i';
		else if (izq->tipoDato == 'f' || der->tipoDato == 'f') tipoDato= 'f';
		else tipoDato= 'v';
		if (sig != NULL) sig->validaTipos();
	}

};


#endif
