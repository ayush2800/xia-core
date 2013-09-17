/*
** Copyright 2013 Carnegie Mellon University
**
** Licensed under the Apache License, Version 2.0 (the "License");
** you may not use this file except in compliance with the License.
** You may obtain a copy of the License at
**
**    http://www.apache.org/licenses/LICENSE-2.0
**
** Unless required by applicable law or agreed to in writing, software
** distributed under the License is distributed on an "AS IS" BASIS,
** WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
** See the License for the specific language governing permissions and
** limitations under the License.
*/

#ifndef SSL_MODULE_H
#define SSL_MODULE_H

#include "SessionModule.h"

class SSLModule : public SessionModule {
	protected:
		bool preSend(void *context, void *rv);
};

class SSLModuleXIA : public SSLModule {
	public:
		void decide(session::SessionInfo *sinfo, UserLayerInfo &userInfo, 
												 AppLayerInfo &appInfo, 
												 TransportLayerInfo &transportInfo, 
												 NetworkLayerInfo &netInfo, 
												 LinkLayerInfo &linkInfo, 
												 PhysicalLayerInfo &physInfo);

		bool breakpoint(Breakpoint breakpoint, void *context, void *rv);
};

class SSLModuleIP : public SSLModule {
	public:
		void decide(session::SessionInfo *sinfo, UserLayerInfo &userInfo, 
												 AppLayerInfo &appInfo, 
												 TransportLayerInfo &transportInfo, 
												 NetworkLayerInfo &netInfo, 
												 LinkLayerInfo &linkInfo, 
												 PhysicalLayerInfo &physInfo);

		bool breakpoint(Breakpoint breakpoint, void *context, void *rv);
};

#endif /* SSL_MODULE_H */
