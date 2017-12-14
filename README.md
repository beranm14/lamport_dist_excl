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


## Shared Variable

For shared variable, there is Lamport Paxos algorithm (see [Computerphille video](https://www.youtube.com/watch?v=s8JqcZtvnsM)). It works pretty similar to locks.

In the same way as the lock are requested: all the nodes keep sorted queue. The node which propose new variable sends requests, collects answers and pick the one with the biggest logical time. In case all the nodes create request in the same time, node `id` comes into to computations and queue is sorted by `id` also.

The resulting variable shared by all is the one with the biggest logical time and from node with the highest `id`

## Usage

For locking example you can use `example.py`, there is working example in `docker-compose.yml`.  **Currently** there are some reserves since Lamport Bakery algorithm give priority to the lowest timestamp, not the biggest (raise condition can force nodes not to get the lock at all).

For sharing variable you can use `var_simulator.py` (implemented from Lamport Paxos alg.).

 * First you have to define nodes in `./lamport/nodes.yml`, which are going to be the nodes to use in the algorithm.
 * Secod you have give `id` argument to the script: `python3 var_simulator.py -w 127.0.0.1:8991`, where `id` is one of the node from `nodes.yml`.
 
 After starting all the nodes, you start to type into to keyboard and all the nodes have to start share the variable.
 
 



