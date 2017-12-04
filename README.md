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

Whole process uses Lamport logical time to keep track of distributed events. Source [Wikipedia](https://en.wikipedia.org/wiki/Lamport_timestamps):

The algorithm follows some simple rules:
  * A process increments its counter before each event in that process;
  * When a process sends a message, it includes its counter value with the message;
  * On receiving a message, the counter of the recipient is updated, if necessary, to the greater of its current counter and the timestamp in the received message. The counter is then incremented by 1 before the message is considered received.

In a Pseudocode format, the algorithm for sending:
```
time = time+1;
time_stamp = time;
send(message, time_stamp);
```

The algorithm for receiving a message:

```
(message, time_stamp) = receive();
time = max(time_stamp, time)+1;
```
