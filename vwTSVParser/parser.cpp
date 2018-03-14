#include "parser.h"

/* implemenation of the tokenizer */
std::vector<std::string> tokenizeCString(char *cstring, char delims[]) {
  // empty vector for results
  std::vector<std::string> output(0);
  char *tok;
  // strtok is a state-function: after you pass the NULL ptr
  tok = strtok(cstring,delims);
  while(tok != NULL) {
    // clean up spaces from the token string
    output.push_back(std::string(popCString(tok,(char*)" ")));
    tok = strtok(NULL,delims);
  }
  return output;
}

/* implementation of a function which deletes elements specific characters from a string */
char* popCString(const char* cstring, char charsToPop[]) {
  // we need to find how many elements will be deleted
  int numToPop = 0;
  const char *c = cstring;
  while(*c){
    char *p = charsToPop;
    while(*p) {
      // iterate over the elements to delete
      if(*c == *p++) {
	numToPop++;
	break;
      }
    }
    c++;
  }

  // allocate output
  char* output = (char*)calloc(std::max(int(strlen(cstring)-numToPop),0)+1, sizeof(char));
  // this skips missing characters
  char *o = output;
  c = cstring;
    while(*c) {
    char *p = charsToPop;
    // if toCopy = true we will copy the current character
    bool toCopy = true;
    while(*p) {
      // see if we need to skip a character
      if(*c == *p++) {
	toCopy = false;
	break;
      }
    }
    if(toCopy) {
      *o = *c;
      o++;
    }
    c++;
  }
    // null termination of C-string
    *o = 0;
    return output;
}

/* implementation of the Feature class */
Feature::Feature(std::string name, feaType Type, std::string value,
	Namespace nameSpace)
  : _name(name), _type(Type), _value(value), _namespace(nameSpace) {}

std::string Feature::getName() const {return _name; }
Feature::feaType Feature::getType() const { return _type; }
std::string Feature::getValue() const { return _value; }
Namespace Feature::getNamespace() const { return _namespace; }
// note here that namespaces are nested
Namespace::NamespaceError::NamespaceError(std::string eMessage) :errorMessage(eMessage) {}

/* implementation of Namespace class */
Namespace::Namespace(std::string name): _name(name), _weight(1.0), _weight_unset(true), _featureVec() {};
Namespace::Namespace(std::string name, double weight): _name(name), _weight(weight), _weight_unset(false), _featureVec() {};
std::string Namespace::getName() const { return _name; }
const double Namespace::getWeight() const {return _weight; }
void Namespace::setWeight(double weight) {
  if(!_weight_unset) throw Namespace::NamespaceError("Trying resetting weight for Namespace");
  _weight = weight;
  _weight_unset = false;
}
void Namespace::addFeature(const Feature* feature) { _featureVec.push_back(feature); }

/* implementation of Label class */
Label::Label(labelType type, std::string value) : _type(type), _value(value) {}
Label::labelType Label::getType() const { return _type; }
std::string Label::getValue() const { return _value; }

