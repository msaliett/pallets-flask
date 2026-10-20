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
	    +int id
	    +String username
	    +String password
	    +register()
	    +login()
    }

    class Post {
	    +int id
	    +int author_id
	    +Timestamp created
	    +String title
	    +String body
	    +create()
	    +update()
	    +delete()
    }

    User "1" -- "0..*" Post : escriu / és autor de >
    ```
