from pydantic import BaseModel

class Configuration(BaseModel):
    id:int
    config: str

default_configuration=Configuration(id=0, config="|../repository/TCPNetwork.o,/emergent_web_server/dana/components/net/TCP.o,/emergent_web_server/repository/request/RequestHandler.o,/emergent_web_server/repository/app_protocols/HTTPProtocol.o,/emergent_web_server/repository/http/HTTPHeader1_0.o,/emergent_web_server/repository/http/handler/GET/HTTPGETCMP.o,/emergent_web_server/dana/components/io/File.o,/emergent_web_server/repository/compression/ZLIB.o,/emergent_web_server/dana/components/os/Run.o,/emergent_web_server/dana/components/time/DateUtil.o,/emergent_web_server/repository/http/util/HTTPUtil.o,/emergent_web_server/dana/components/data/StringUtil.o,/emergent_web_server/dana/components/data/adt/List.o|0:net.TCPSocket:1,0:net.TCPServerSocket:1,0:request.RequestHandler:2,2:app_protocols.AppProtocol:3,3:http.HTTPHeader:4,4:http.handler.GET.HTTPGET:5,5:io.File:6,5:compression.Compression:7,7:os.Run:8,7:time.DateUtil:9,7:io.FileSystem:6,4:http.util.HTTPUtil:10,10:io.FileSystem:6,10:data.StringUtil:11,11:data.adt.List:12|")
