import "websocket_client.dart";
import "formats.dart";
import "dart:convert";

/* Big things we need from dart:
 *  - websocket connector
 *  - representation for the user state (ie, who they are, how much they're making, what they're doing, etc)
 *  - Framework display class to be overwritten (probably a separate file. . .)
 *  - Intractable bits?
*/

void main()
{
  var wsTest = websocket_client('ws://localhost:4502', "Hello?");
  var guest = new User(json.encode({"commander":"Caddox", "credits": 182319}));

  Form site_form = new Startup(guest);
}

