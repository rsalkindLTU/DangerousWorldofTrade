import "dart:html";
import "dart:convert";

class User
{
  String _commander_name;
  BigInt _current_credits;
  List<String> _cargo;// May not end up using this one. . .

  // User class is going to contain some user information
  User(String json_rep)
  {
    print("Creating user object. . .");
    if(json_rep == '' || json_rep == null)
    {
      this._commander_name = "";
      this._current_credits = new BigInt.from(0);
      this._cargo = [''];
    }
    else
    { // Json string is an actual thing!
      var user_json = jsonDecode(json_rep);
      this._commander_name = user_json['commander'];
      this._current_credits = new BigInt.from(user_json['credits']);
      this._cargo = user_json['cargo'];
    }
  }

  void update_cargo(List<String> newCargo)
  {
    // Updates the cargo list of the user.
    _cargo = newCargo;
  }

  void update_credits(int credits)
  {
    _current_credits = BigInt.from(credits);
  }
}


class websocket_client
{
  final WebSocket _socket;

  websocket_client(String url, String fstMsg) : _socket = WebSocket(url)
  {
    print("Connecting to $url. . . ");
    _listen(fstMsg);
  }

  void send (String value)
  {
    print("==> $value");
    _socket.send(value);
  }

  void _listen(String firstMsg) 
  {
    _socket.onOpen.listen((e) 
                          {
                            print("Connected!");
                            send(firstMsg);
                          });
    _socket.onClose.listen((_) => print("Goodbye!"));
    _socket.onError.listen((_) => print('Error opening connection :('));

    _socket.onMessage.listen(
      (e)
      {
        print("<== ${e.data}");
        addToFooter(e.data);
        //send(e.data);
      }
    );
  }
}

void addToFooter(String data)
{
  var footerList = querySelector('.footer');
  var newItem = new UListElement();
  newItem.text = data;
  footerList.children.insert(0, newItem);
  //footerList.children.add(newItem);
}

void main() async {
  var wsTest = websocket_client('ws://localhost:4502', "Hello?");

  InputElement input = querySelector("input");


  var out = querySelector("#name_out");
  input.onChange.listen((_) {
    wsTest.send(input.value);
    out.text = "Hello ${input.value}!";
    input.value = '';
  });

}

/* Big things we need from dart:
 *  - websocket connector
 *  - representation for the user state (ie, who they are, how much they're making, what they're doing, etc)
 *  - Framework display class to be overwritten (probably a separate file. . .)
 *  - Intractable bits?
*/
