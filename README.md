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

The resulting variable shared by all is the one with the biggest logical time and from a node with the highest `id`. That is the change in Paxos since lock should be obtained by the process with the lowest timestamp (and `id` if needed).

### Tests

For sharing variable you can use `var_simulator.py` (implemented from Lamport Paxos alg.).

 * First you have to define nodes in `./lamport/nodes.yml`, which are going to be the nodes to use in the algorithm.
 * Secod you have give `id` argument to the script: `python3 var_simulator.py -w 127.0.0.1:8991`, where `id` is one of the node from `nodes.yml`.
 
After starting all the nodes, you start to type into to keyboard and all the nodes have to start share the variable.
 
### Locking & Unlocking with Lamport bakery algoritm

For locking example you can use `example.py`, there is working example in `docker-compose.yml` (start with `docker-compose up`). It goes through two tests:

 * First test:

Synchronize all the threads to the seconds and give them random value in interval of 0-1 second, then start them and let them take the lock.

 * Second test:

Synchronize all the threads to the next 1 minute and half in the future (it is done by pause module, this weird interval is done cause we have to wait to finnish first test). If current time is 14.45, next test will start at 15.30. Give no space of random start. Start all the threads at once and wait until it all finnishes.

Correct result should show following (output of `logging` module ommited):

```
runner3_1  | ==================================================================
runner3_1  | ==================  GETTING FIRST LOCK ===========================
runner3_1  | MULTIPLE PROCESSES TRY TO GET THE LOCK WITH LITTLE TIME DIFFERENCE
runner3_1  | ==================================================================
runner3_1  | Setting same time till 2017-12-14 22:14:09
runner3_1  | Locked
runner3_1  | Unlocked
runner3_1  | ==================================================================
runner3_1  | ==================================================================
runner3_1  | =================  GETTING SECOND LOCK ===========================
runner3_1  | MULTIPLE PROCESSES TRY TO GET THE LOCK WITH AT THE SAME TIME
runner3_1  | ==================================================================
runner3_1  | Setting same time till 2017-12-14 22:15:00
runner3_1  | Couldn't get a lock
runner3_1  | ==================================================================
runner3_1  | ==================================================================
runner3_1  | ==================================================================

runner2_1  | ==================================================================
runner2_1  | ==================  GETTING FIRST LOCK ===========================
runner2_1  | MULTIPLE PROCESSES TRY TO GET THE LOCK WITH LITTLE TIME DIFFERENCE
runner2_1  | ==================================================================
runner2_1  | Setting same time till 2017-12-14 22:14:09
runner2_1  | Couldn't get a lock
runner2_1  | ==================================================================
runner2_1  | ==================================================================
runner2_1  | =================  GETTING SECOND LOCK ===========================
runner2_1  | MULTIPLE PROCESSES TRY TO GET THE LOCK WITH AT THE SAME TIME
runner2_1  | ==================================================================
runner2_1  | Setting same time till 2017-12-14 22:15:00
runner2_1  | Couldn't get a lock
runner2_1  | ==================================================================
runner2_1  | ==================================================================
runner2_1  | ==================================================================

runner1_1  | ==================================================================
runner1_1  | ==================  GETTING FIRST LOCK ===========================
runner1_1  | MULTIPLE PROCESSES TRY TO GET THE LOCK WITH LITTLE TIME DIFFERENCE
runner1_1  | ==================================================================
runner1_1  | Setting same time till 2017-12-14 22:14:09
runner1_1  | Couldn't get a lock
runner1_1  | ==================================================================
runner1_1  | ==================================================================
runner1_1  | =================  GETTING SECOND LOCK ===========================
runner1_1  | MULTIPLE PROCESSES TRY TO GET THE LOCK WITH AT THE SAME TIME
runner1_1  | ==================================================================
runner1_1  | Setting same time till 2017-12-14 22:15:00
runner1_1  | Locked
runner1_1  | Unlocked
runner1_1  | ==================================================================
runner1_1  | ==================================================================
runner1_1  | ==================================================================

```


As we can see, in first test process `runner3_1` got the lock. After 10 seconds it got released and second test started. We can see that second test was won by the `runner1_1`. Incorrect result would be that multiple processes take the lock or none of them would take one.





