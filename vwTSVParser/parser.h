#include<iostream>
#include<stdlib.h>
#include<cstring>
#include<vector>

// Tokenizer for C strings

std::vector<std::string> tokenizeCString(char *cstring, char delims[] = (char*)",");

// character poppper for C strings
char* popCString(const char cstring[], char charsToPop[] = (char*)")(");  

// forward declaration to trick the compiler
class Feature;

class Namespace {
  std::string _name;
  double _weight;
  bool _weight_unset; // true when in the formatting file
  // the weight was set to a val
  // Namespace stores reference to immutable features
  std::vector<const Feature*> _featureVec;
 public:
  struct NamespaceError {
    std::string errorMessage;
    NamespaceError(std::string eMessage);
  };
  
  Namespace(std::string name);
  Namespace(std::string name, double weight);
  std::string getName() const;
  const double getWeight() const;
  void setWeight(double weight);
  void addFeature(const Feature* feature);
};

class Feature {
 public:
  enum feaType {categorical, numerical};
  
 private:
  std::string _name;
  feaType _type;
  std::string _value;
  Namespace _namespace;

 public:
  Feature(std::string name, feaType Type, std::string value,
	  Namespace nameSpace);
  std::string getName() const;
  feaType getType() const;
  std::string getValue() const;
  Namespace getNamespace() const;
};

class Label {
 public:
  enum labelType {label, importance, base, tag};

 private:
  labelType _type;
  std::string _value;

 public:
  Label(labelType type, std::string value);
  labelType getType() const;
  std::string getValue() const;
};



