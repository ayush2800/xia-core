#include <string>
#include <vector>
#include <iostream>
#include <thread>
#include "Xkeys.h"
#include "Xsocket.h"
#include "dagaddr.h"
#include "dagaddr.hpp"
#include "XIARouter.hh"

#define MB(__mb) (KB(__mb) * 1024)
#define KB(__kb) ((__kb) * 1024)
#define CHUNKSIZE MB(1)

using namespace std;

int main(int argc, char *argv[]){
	if(argc != 2){
		printf("must have a file name\n");
		exit(-1);
	}

	int count;
	sockaddr_x *addrs = NULL;
	if ((count = XputFile(&xcache, argv[1], CHUNKSIZE, &addrs)) < 0) {
		warn("unable to serve the file: %s\n", argv[1]);
		exit(-1);
	}

	Graph g(addrs);
	say("CID dag: %s\n", g.dag_string().c_str());

	while(1){};
	return 0;
}