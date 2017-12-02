# Lamport Distributed Exclusion

This repository is for seminar work of MI-DSV at CTU. Main result should be implementation of Lamport Distributed Exclusion algorithm in Python using Python's sockets. Result should be able to share variable between multiple nodes of distributed system.


## Algorithm description

Copy from [Wikipedia](https://en.wikipedia.org/wiki/Lamport%27s_distributed_mutual_exclusion_algorithm):


Requesting process:
  * Pushing its request in its own queue (ordered by time stamps)
  * Sending a request to every node.
  * Waiting for replies from all other nodes.
  * If own request is at the head of its queue and all replies have been received, enter critical section.
  * Upon exiting the critical section, remove its request from the queue and send a release message to every process.

Other processes:
  * After receiving a request, pushing the request in its own request queue (ordered by time stamps) and reply with a time stamp.
  * After receiving release message, remove the corresponding request from its own request queue.
  * If own request is at the head of its queue and all replies have been received, enter critical section.
