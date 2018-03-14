#include<getopt.h>
#include<iostream>
#include<stdlib.h>
#include<fstream>
#include "parser.h"
#include<map>

extern char *optarg;
extern int optind, opterr, optopt;

// format for command line options
// --file abc.txt (required)
// --sep="::" (optional, default = '\t')
static struct option long_options[] = {
  {"format", required_argument,  0, 'f'},
  {"sep", optional_argument, 0, 's'},
  {0, 0, 0, 0}
};

// hold the file with format and separator
std::string formatFile; // file name for format
std::string separator; // separator

// map with label components to be filled and parsed
std::map<std::string,const Label*> labelMap;

// map with namespaces
std::map<std::string,Namespace*> namespaceMap;

int main (int argc, char **argv) {
  while(true) {
    int option_index = 0;
  int c;
  c = getopt_long(argc, argv, "f:s:", long_options, &option_index);
  if (c == -1)
    break;
  switch(c) {
  case 'f':
    formatFile = std::string(optarg);
    break;
  case 's':
    if(optarg) separator = std::string(optarg);
    else separator = "\t";		 
    break;
    }
  }

  // if no format file terminate
  if(formatFile.size() == 0) return 0;

  // Read formatFile
  std::string line;
  std::ifstream fin;
  fin.open(formatFile.c_str(), std::ios::in);
  while(!fin.eof()) {
    std::getline(fin,line);
    std::cout << line << std::endl;
    char* poppedLine = popCString(line.c_str());
    std::cout << poppedLine << std::endl;
    std::vector<std::string> lineToken = tokenizeCString(poppedLine);
    for(std::vector<std::string>::iterator b = lineToken.begin(); b != lineToken.end(); b++) {
      std::cout << *b << std::endl;
    }
  }
  fin.close();

  // initialize the labelMap
  labelMap["label"] = NULL;
  labelMap["importance"] = NULL;
  labelMap["base"] = NULL;
  labelMap["tag"] = NULL;

  
  return 0;
}
