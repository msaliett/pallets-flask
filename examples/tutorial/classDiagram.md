```mermaid
---
config:
  layout: dagre
  theme: redux-color
  class:
    hideEmptyMembersBox: false
---
classDiagram
direction LR
    class User {
	    +id: int
	    +username: String
	    +password:String
	    +register()
	    +login()
    }

    class Post {
	    +id: int
	    +author_id: int
	    +created: Timestamp
	    +title: String 
	    +body: String 
	    +create()
	    +update()
	    +delete()
    }

    User "1" -- "0..*" Post : escriu / és autor de >
    ```
