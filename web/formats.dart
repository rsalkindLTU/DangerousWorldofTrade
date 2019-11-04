import "dart:html";
//import "dart:convert";
import "websocket_client.dart";

abstract class Form
{
  /* Each class needs access to the header content,
   * the content of the 'content' div tag,
   * and the content of the footer.
   *
   * The content of the footer should not be changed.
   *
   * These are hard coded references for now(?)
   */

  final Element header; //= querySelector('.header');
  final Element content; //= querySelector('.content');
  final Element footer; //= querySelector('.footer'); // Should not be changed.

  Form(): header = querySelector('.header'),
          content = querySelector('.content'),
          footer = querySelector('footer');

  // Each Form needs to be able to initialize itself.
  void init();
  void update(String data);

}

/* Class Startup (extending from Form)
 * Provides a simple startup format for times before the server
 * begins to provide much data to the client.
 *
 */
class Startup extends Form
{
  String _commander_name;
  var _user_reference;

  // Displays startup information, like the commander name and where they are
  Startup(User user)
  {
    this._commander_name = user.commander_name;
    this._user_reference = user;
    this.init();
  }

  void init()
  {
    // Set the header to a greeting.
    super.header.children.clear();
    var header_p = elementFactory('p', "Hello Commander ${_commander_name}!");
    super.header.children.add(header_p);

    super.content.children.clear(); // Clear the content section
    var item_p = elementFactory("p", "Looks like we don't have info for you!");
    var credit_count_p = elementFactory("p", 'You currently have ${_user_reference.credits} credits.');
    super.content.children.add(item_p);
    super.content.children.add(credit_count_p);
  }

  // Update the current display based on JSON string data.
  void update(String data)
  {
    var newItem = new UListElement();
    newItem.text = data;
    super.footer.children.insert(0, newItem);
  }
}

class Traveling extends Form
{
  User _user_reference;
  String _destination;

  Traveling(User user)
  {
    this._user_reference = user;
    this._destination = "Unknown";
  }

  void init()
  {
    // Setup the header.
    super.header.children.clear();
    var head_h1 = elementFactory('h1', 'Traveling to ${this._destination}. . .');
    var head_h2 = elementFactory('h2', 'Safe travels Commander!');
    super.header.children.add(head_h1);
    super.header.children.add(head_h2);

    // Setup the content
    super.content.children.clear();
    super.content.children.add(elementFactory('p', "There really is nothing here yet. Don't be sad!"));
  }

  void update(String data)
  {
    print("Class Traveling does not have update implemented yet");
    print("Was passed: ${data}");
  }
}

class Trading extends Form
{
  // We need a user reference, a location, a destination,
  // a cargo, a running profit total
  User _user_reference;
  String _destination;
  String _location;
  List<String> _cargo;
  num _total_profit;

  void init()
  {
    print("Class Trading has not implemented init yet.");
  }

  void update(String data)
  {
    print("Class Trading has not implemented update yet.");
    print("The following data was passed: ${data}");
  }
}
