import "dart:html";
import "dart:convert";
import "formats.dart";

/* Class: User
 * Description: This class describes a commander, including their name, 
 * worth, and potentially other things if I choose to add them. In essence,
 * it becomes a wrapper for the state for the user.
 */
class User
{
  String _commander_name;
  num _current_credits;

  // User class is going to contain some user information
  User(String json_rep)
  {
    print("Creating user object. . .");
    // If we do not have access to a json string with the user information,
    // we need to have placeholders for later
    if(json_rep == '' || json_rep == null)
    {
      this._commander_name = "";
      this._current_credits = 0;
    }
    else
    { // Json string is an actual thing!
      var user_json = jsonDecode(json_rep);
      this._commander_name = user_json['commander'];
      this._current_credits = user_json['credits'];
    }
  }

  // Getters and setters
  void set credits(num credits)
  {
    _current_credits = credits;
  }

  num get credits
  {
    return this._current_credits;
  }

  void set commander_name(String name)
  {
    this._commander_name = name;
  }

  String get commander_name
  {
    return this._commander_name;
  }

  User get user
  {
    return this;
  }

  /* Gets the object as a JSON string. May be incorrect for now. */
  String as_json()
  {
    return json.encode({
        "commander": this._commander_name,
        "credits"  : this._current_credits,
    });
  }
}

/* Class: websocket_client
 * Description: This class wraps the websocket connection to the server.
 * It is able to send messages and receive them, and will eventually
 * wrap what gets parsed and when.
 */
class websocket_client
{
  final WebSocket _socket;

  // Constructor doing constructor things.
  websocket_client(String url, String fstMsg) : _socket = WebSocket(url)
  {
    print("Connecting to $url. . . ");
    _listen(fstMsg);
  }

  /* Function to send a string value to the sever from the client */
  void send (String value)
  {
    print("==> $value");
    _socket.send(value);
  }

  /* Function that handles all the potential outcomes of the websocket */
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

/* A helper function to add data to the footer of the document. */
void addToFooter(String data)
{
  var footerList = querySelector('.footer');
  var newItem = new UListElement();
  newItem.text = data;
  footerList.children.insert(0, newItem);
  //footerList.children.add(newItem);
}

// Simple function that creates a HTML item like a factory.
Element elementFactory(String tag, String text)
{
    Element item = new Element.tag(tag);
    item.text = text;
    return item;
}

