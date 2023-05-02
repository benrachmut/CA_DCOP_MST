import abc
import threading
from abc import ABC
debug_print_for_distribution = True




class UnboundedBuffer():

    def __init__(self):

        self.buffer = []

        self.cond = threading.Condition(threading.RLock())

    def insert(self, list_of_msgs):

        with self.cond:
            self.buffer.append(list_of_msgs)
            self.cond.notify_all()

    def extract(self):

        with self.cond:

            while len(self.buffer) == 0:
                self.cond.wait()

        ans = []

        for msg in self.buffer:

            if msg is None:

                return None

            else:

                ans.append(msg)

        self.buffer = []

        return ans

    def is_buffer_empty(self):

        return len(self.buffer) == 0

class Msg():

    def __init__(self, sender, receiver, information, is_with_perfect_communication):
        self.sender = sender

        self.receiver = receiver

        self.information = information

        self.msg_time = None

        self.timestamp = None

        self.is_with_perfect_communication =is_with_perfect_communication

    def set_time_of_msg(self, delay):
        self.msg_time = self.msg_time + delay

    def add_current_NCLO(self, NCLO):
        self.msg_time = NCLO

    def add_timestamp(self, timestamp):
        self.timestamp = timestamp


class ClockObject():
    def __init__(self):
        self.clock = 0.0
        self.lock = threading.RLock()
        self.idle_time = 0.0

    def change_clock_if_required(self, time_of_received_msg: float):
        with self.lock:
            if self.clock < time_of_received_msg:
                self.idle_time = self.idle_time + (time_of_received_msg - self.clock)
                self.clock = time_of_received_msg

    def increment_clock(self, atomic_counter: int):
        with self.lock:
            self.clock = self.clock + atomic_counter

    def get_clock(self):
        with self.lock:
            return self.clock



class Mailer(threading.Thread):

    def __init__(self, f_termination_condition, f_global_measurements,
                 f_communication_disturbance):
        threading.Thread.__init__(self)

        self.id_ = 0
        self.msg_box = []

        # function that returns dict=  {key: str of fields name,function of calculated fields}
        self.f_global_measurements = f_global_measurements
        # function that returns None for msg loss, or a number for NCLO delay
        self.f_communication_disturbance = f_communication_disturbance

        # function received by the user that determines when the mailer should stop iterating and kill threads
        self.f_termination_condition = f_termination_condition

        # TODO update in solver, key = agent, value = buffer  also points as an inbox for the agent
        self.agents_outboxes = {}

        # TODO update in solver, buffer also points as out box for all agents
        self.inbox = None

        # the algorithm agent created by the user will be updated in reset method
        self.agents_algorithm = []

        # mailer's clock
        self.time_mailer = ClockObject()

        self.measurements = {}

        # message loss due to communication protocol
        self.msg_not_delivered_loss_counter = 0

        # message loss due to timestamp policy
        self.msg_not_delivered_loss_timestamp_counter = 0

        # message sent by players regardless to communication protocol
        self.msg_sent_counter = 0

        # messages that arrive to their destination
        self.msg_received_counter = 0

        self.last_time = 0
        self.delta_time = 9999999

    def get_allocation_dictionary(self):
        pass

    def reset(self,tnow):
        global mailer_counter
        self.msg_box = []
        mailer_counter = mailer_counter + 1
        self.id_ = mailer_counter
        self.agents_outboxes = {}  # TODO update in allocate
        self.inbox = None  # TODO update in solver
        self.time_mailer = ClockObject()
        self.measurements = {}
        self.msg_not_delivered_loss_counter = 0
        self.msg_not_delivered_loss_timestamp_counter = 0
        self.msg_sent_counter = 0
        self.msg_received_counter = 0

        for key in self.f_global_measurements.keys():
            self.measurements[key] = {}
        self.measurements["Loss Counter"] = {}
        self.measurements["Loss Timestamp Counter"] = {}
        self.measurements["Message Sent Counter"] = {}
        self.measurements["Message Received Counter"] = {}

        for aa in self.agents_algorithm:
            aa.reset_fields(tnow)

        self.last_time = 0
        self.delta_time = 0
    def add_out_box(self, key: str, value: UnboundedBuffer):
        self.agents_outboxes[key] = value

    def set_inbox(self, inbox_input: UnboundedBuffer):
        self.inbox = inbox_input


    def remove_agent(self,entity_input):

        for agent in self.agents_algorithm:
            if agent.simulation_entity.id_ == entity_input.id_:
                self.agents_algorithm.remove(agent)
                return


    def run(self) -> None:

        """

        create measurements

        iterate for the first, in constractor all agents initiate their first "synchrnoized" iteration

        iteration includes:

        -  extract msgs from inbox: where the mailer waits for msgs to be sent

        -  place messages in mailers message box with a withdrawn delay

        -  get all the messages that have delivery times smaller in comperision to the the mailers clock

        - deliver messages to the algorithm agents through their unbounded buffer



        the run continue to iterate, and creates measurements at each iteration until the given termination condition is met

        :return:

        """

        self.create_measurements()

        self.mailer_iteration(with_update_clock_for_empty_msg_to_send=True)

        while not self.f_termination_condition(self.agents_algorithm, self):

            self.create_measurements()

            self.self_check_if_all_idle_to_continue()

            self.mailer_iteration(with_update_clock_for_empty_msg_to_send=False)



        self.kill_agents()

        for aa in self.agents_algorithm:
            aa.join()

    def create_measurements(self):
        current_clock = self.time_mailer.get_clock()  # TODO check if immutable
        #print("line 257 ",current_clock)


        for measurement_name, measurement_function in self.f_global_measurements.items():

            measured_value = measurement_function(self.agents_algorithm)

            self.measurements[measurement_name][current_clock] = measured_value



        self.measurements["Loss Counter"][current_clock] = self.msg_not_delivered_loss_counter
        self.measurements["Loss Timestamp Counter"][current_clock] = self.get_counter_sum_of_timestamp_loss_msgs_from_agents()
        self.measurements["Message Sent Counter"][current_clock] = self.msg_sent_counter
        self.measurements["Message Received Counter"][current_clock] = self.get_counter_sum_msg_received_counter_from_agents()

    @staticmethod
    def get_data_keys():
        return ["Loss Counter","Loss Timestamp Counter","Message Sent Counter","Message Received Counter"]

    def get_counter_sum_of_timestamp_loss_msgs_from_agents(self):
        ans = 0
        for aa in self.agents_algorithm:
            ans+=aa.msg_not_delivered_loss_timestamp_counter
        return ans

    def get_counter_sum_msg_received_counter_from_agents(self):
        ans = 0
        for aa in self.agents_algorithm:
            ans += aa.msg_received_counter
        return ans

    def kill_agents(self):

        for out_box in self.agents_outboxes.values():
            out_box.insert(None)

    def self_check_if_all_idle_to_continue(self):

        while self.inbox.is_buffer_empty() :

            are_all_idle = self.are_all_agents_idle()

            is_inbox_empty = self.inbox.is_buffer_empty()

            is_msg_box_empty = len(self.msg_box) == 0

            if are_all_idle and is_inbox_empty and not is_msg_box_empty:
                self.should_update_clock_because_no_msg_received()

                msgs_to_send = self.handle_delay()

                self.agents_receive_msgs(msgs_to_send)

    def mailer_iteration(self, with_update_clock_for_empty_msg_to_send):


        self.last_time = self.time_mailer.clock

        msgs_from_inbox = self.inbox.extract()

        self.place_msgs_from_inbox_in_msgs_box(msgs_from_inbox)

        if with_update_clock_for_empty_msg_to_send:
            self.should_update_clock_because_no_msg_received()

        msgs_to_send = self.handle_delay()

        self.agents_receive_msgs(msgs_to_send)

        self.delta_time = self.time_mailer.clock-self.last_time

    def handle_delay(self):

        """

        get from inbox all msgs with msg_time lower then mailer time

        :return: msgs that will be delivered

        """

        msgs_to_send = []

        new_msg_box_list = []
        current_clock = self.time_mailer.get_clock()  # TODO check if immutable

        for msg in self.msg_box:
            if msg.msg_time <= current_clock:
                msgs_to_send.append(msg)
            else:
                new_msg_box_list.append(msg)
        self.msg_box = new_msg_box_list
        return msgs_to_send

    def place_msgs_from_inbox_in_msgs_box(self, msgs_from_inbox):

        """

        take a message from message box, and if msg is not lost, give it a delay and place it in msg_box

        uses the function recieves as input in consturctor f_communication_disturbance

        :param msgs_from_inbox: all messages taken from inbox box

        :return:

        """

        for msgs in msgs_from_inbox:
            if isinstance(msgs, list):
                for msg in msgs:
                    self.place_single_msg_from_inbox_in_msgs_box(msg)
            else:
                self.place_single_msg_from_inbox_in_msgs_box(msgs)

    def place_single_msg_from_inbox_in_msgs_box(self,msg):
        self.update_clock_upon_msg_received(msg)


        communication_disturbance_output = self.f_communication_disturbance(e1,e2)
        flag = False
        self.msg_sent_counter += 1
        if msg.is_with_perfect_communication:
            self.msg_box.append(msg)
            flag = True

        if not flag and communication_disturbance_output is not None:
            delay = communication_disturbance_output
            delay = int(delay)

            msg.set_time_of_msg(delay)
            if debug_print_for_distribution:
                print(delay)
            self.msg_box.append(msg)

        if communication_disturbance_output is None:
            self.msg_not_delivered_loss_counter +=1




    def update_clock_upon_msg_received(self, msg: Msg):

        """
        prior for msg entering to msg box the mailer's clock is being updated
        if the msg time is larger than
        :param msg:
        :return:

        """

        msg_time = msg.msg_time
        self.time_mailer.change_clock_if_required(msg_time)


    def agents_receive_msgs(self, msgs_to_send):

        """
        :param msgs_to_send: msgs that their delivery time is smaller then the mailer's time
        insert msgs to relevant agent's inbox
        """
        msgs_dict_by_reciever_id = self.get_receivers_by_id(msgs_to_send)


        for node_id, msgs_list in msgs_dict_by_reciever_id.items():
            node_id_inbox = self.agents_outboxes[node_id]
            node_id_inbox.insert(msgs_list)

    def get_receivers_by_id(self, msgs_to_send):

        '''

        :param msgs_to_send: msgs that are going to be sent in mailer's current iteration

        :return:  dict with key = receiver and value = list of msgs that receiver need to receive

        '''

        receivers_list = []

        for msg in msgs_to_send:
            receivers_list.append(msg.receiver)

        receivers_set = set(receivers_list)

        ans = {}

        for receiver in receivers_set:

            msgs_of_receiver = []

            for msg in msgs_to_send:
                if msg.receiver == receiver:
                    msgs_of_receiver.append(msg)
            ans[receiver] = msgs_of_receiver

        return ans

    @staticmethod
    def msg_with_min_time(msg: Msg):

        return msg.msg_time

    def should_update_clock_because_no_msg_received(self):

        """

        update the mailers clock according to the msg with the minimum time from the mailers message box

        :return:

        """

        msg_with_min_time = min(self.msg_box, key=Mailer.msg_with_min_time)

        msg_time = msg_with_min_time.msg_time
        self.time_mailer.change_clock_if_required(msg_time)


    def are_all_agents_idle(self):

        for a in self.agents_algorithm:

            if not a.get_is_idle():
                return False

        return True



    def get_simulation_entity(self, id_looking_for):
        for a in self.agents_algorithm:
            if a.simulation_entity.id_ == id_looking_for:
                return a.simulation_entity


class Location:
    def __init__(self,x,y):
        self.x = x
        self.y = y




class Entity():
    def __init__(self,id_ , location:Location):
        self.location = location
        self.id_ = id_


class TargetSimulation(Entity):
    def __init__(self,id_,location):
        Entity.__init__(self,"A_"+id_,location)

class AgentSimulation(Entity):
    def __init__(self,id_,location,domain,neighbours_ids_list = []):
        Entity.__init__(self,id_,location)
        self.domain = domain# location.get_domain()
        self.neighbours_ids_list = neighbours_ids_list

        
class AgentAlgorithm(threading.Thread, ABC):
    """
    list of abstract methods:
    initialize_algorithm
    --> how does the agent begins algorithm prior to the start() of the thread

    set_receive_flag_to_true_given_msg(msgs):
    --> given msgs received is agent going to compute in this iteration

    get_is_going_to_compute_flag()
    --> return the flag which determins if computation is going to occur

    update_message_in_context(msg)
    --> save msgs in agents context

    compute
    -->  use updated context to compute agents statues and

    get_list_of_msgs
    -->  create and return list of msgs

    get_list_of_msgs
    --> returns list of msgs that needs to be sent

    set_receive_flag_to_false
    --> after computation occurs set the flag back to false

    measurements_per_agent
    --> returns dict with key: str of measure, value: the calculated measure
    """

    def __init__(self, simulation_agent:AgentSimulation, is_with_timestamp=True):

        threading.Thread.__init__(self)
        
        self.is_with_timestamp = is_with_timestamp  # is agent using timestamp when msgs are received
        self.timestamp_counter = 0  # every msg sent the timestamp counter increases by one (see run method)
        self.simulation_entity = simulation_agent  # all the information regarding the simulation entity
        self.atomic_counter = 0  # counter changes every computation
        self.NCLO = ClockObject()  # an instance of an object with
        self.idle_time = 0
        self.is_idle = True
        self.cond = threading.Condition(threading.RLock())  # TODO update in solver
        self.inbox = None  # DONE TODO update in solver
        self.outbox = None
        self.msg_not_delivered_loss_timestamp_counter = 0
        self.msg_received_counter = 0

    def reset_fields(self,t_now):
        self.t_now = t_now

        self.timestamp_counter = 0  # every msg sent the timestamp counter increases by one (see run method)
        self.atomic_counter = 0  # counter changes every computation
        self.NCLO = ClockObject()  # an instance of an object with
        self.idle_time = 0
        self.is_idle = True
        self.cond = threading.Condition(threading.RLock())
        self.inbox = None  # DONE
        self.outbox = None
        self.reset_additional_fields()
        self.msg_not_delivered_loss_timestamp_counter = 0
        self.msg_received_counter = 0





    def set_inbox(self, inbox_input: UnboundedBuffer):
        self.inbox = inbox_input

    def set_outbox(self, outbox_input: UnboundedBuffer):
        self.outbox = outbox_input






    @abc.abstractmethod
    def initiate_algorithm(self):
        """
        before thread starts the action in this method will occur
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def measurements_per_agent(self):
        """
        NotImplementedError
        :return: dict with key: str of measure, value: the calculated measure
        """
        raise NotImplementedError

    # ---------------------- receive_msgs ----------------------

    def receive_msgs(self, msgs: []):

        for msg in msgs:

            if self.is_with_timestamp:

                current_timestamp_from_context = self.get_current_timestamp_from_context(msg)

                if msg.timestamp > current_timestamp_from_context:
                    self.set_receive_flag_to_true_given_msg(msg)
                    self.update_message_in_context(msg)
                    self.msg_received_counter += 1

                else:
                    self.msg_not_delivered_loss_timestamp_counter += 1
            else:
                self.set_receive_flag_to_true_given_msg(msg)
                self.update_message_in_context(msg)
                self.msg_received_counter += 1

        self.update_agent_time(msgs)

    @abc.abstractmethod
    def set_receive_flag_to_true_given_msg(self, msg):

        """
        given msgs received is agent going to compute in this iteration?
        set the relevant computation flag
        :param msg:
        :return:
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_current_timestamp_from_context(self, msg):

        """
        :param msg: use it to extract the current timestamp from the receiver
        :return: the timestamp from the msg
        """

        raise NotImplementedError

    @abc.abstractmethod
    def update_message_in_context(self, msg):

        '''
        :param msg: msg to update in agents memory
        :return:
        '''

        raise NotImplementedError

    # ---------------------- receive_msgs ----------------------

    def update_agent_time(self, msgs):

        """
        :param msgs: list of msgs received simultaneously
        """
        max_time = self.get_max_time_of_msgs(msgs)
        self.NCLO.change_clock_if_required(max_time)

        # if self.NCLO <= max_time:
        #    self.idle_time = self.idle_time + (max_time - self.NCLO)
        #    self.NCLO = max_time

    def get_max_time_of_msgs(self, msgs):
        max_time = 0
        for msg in msgs:
            time_msg = msg.msg_time
            if time_msg > max_time:
                max_time = time_msg

        return max_time

    # ---------------------- reaction_to_msgs ----------------------

    def reaction_to_msgs(self):

        with self.cond:
            self.atomic_counter = 0
            if self.get_is_going_to_compute_flag() is True:
                self.compute()  # atomic counter must change
                self.timestamp_counter = self.timestamp_counter + 1
                self.NCLO.increment_clock(atomic_counter=self.atomic_counter)
                self.send_msgs()
                self.set_receive_flag_to_false()

    @abc.abstractmethod
    def get_is_going_to_compute_flag(self):
        """
        :return: the flag which determines if computation is going to occur
        """
        raise NotImplementedError

    @abc.abstractmethod
    def compute(self):
        """
       After the context was updated by messages received, computation takes place
       using the new information and preparation on context to be sent takes place
        """
        raise NotImplementedError

    def send_msgs(self):
        msgs = self.get_list_of_msgs_to_send()
        for msg in msgs:
            msg.add_current_NCLO(self.NCLO.clock)
            msg.add_timestamp(self.timestamp_counter)
            msg.is_with_perfect_communication = self.check_if_msg_should_have_perfect_communication(msg)
        self.outbox.insert(msgs)

    def check_if_msg_should_have_perfect_communication(self):
        """
        if both agent "sit" on the same computer them true
        :return: bool
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_list_of_msgs_to_send(self):
        """
        create and return list of msgs to send
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_receive_flag_to_false(self):
        """
        after computation occurs set the flag back to false
        :return:
        """
        raise NotImplementedError

    def run(self) -> None:


        while True:

            self.set_idle_to_true()

            msgs_list = self.inbox.extract()  # TODO when finish mailer

            with self.cond:
                if msgs_list is None:
                    break

                msgs = []
                for msg_list in msgs_list:
                    for msg in msg_list:
                        msgs.append(msg)
                self.set_idle_to_false()
                self.receive_msgs(msgs)
                self.reaction_to_msgs()


    def set_idle_to_true(self):

        with self.cond:
            self.is_idle = True

            self.cond.notify_all()

    def set_idle_to_false(self):

        with self.cond:
            self.is_idle = False

    def get_is_idle(self):
        with self.cond:
            while not self.is_idle:
                self.cond.wait()
            return self.is_idle

    @abc.abstractmethod
    def reset_additional_fields(self):
        raise NotImplementedError


class AgentArseni (AgentAlgorithm):
    def __init__(self,simulation_agent:AgentSimulation,value):
        AgentAlgorithm.__init__(self, simulation_agent = simulation_agent)
        self.value = value
        self.to_compute
        self.local_view = {}


    def initiate_algorithm(self):
        self.send_msgs()


    def measurements_per_agent(self):
        pass

    def set_receive_flag_to_true_given_msg(self, msg):
        self.to_compute = True

    def get_current_timestamp_from_context(self, msg):
        return 0

    def update_message_in_context(self, msg):
        sender = msg.sender
        info = msg.information
        self.local_view[sender] = info

    def get_is_going_to_compute_flag(self):
        return  self.to_compute

    def compute(self):
        for d in self.dom
        for n,v in self.local_view.items():


    def get_list_of_msgs_to_send(self):

    def set_receive_flag_to_false(self):



if __name__ == '__main__':
    
    a1 = AgentSimulation("1",Location(0,0),domain=["a","b"])
    a2 = AgentSimulation("2",Location(10,10),domain=["a","b"])
    a3 = AgentSimulation("3",Location(5,5),domain=["a","b"])

    a1.neighbours_ids_list=["2","3"]
    a2.neighbours_ids_list=["1","3"]
    a3.neighbours_ids_list=["2","3"]

    aa1 = AgentArseni(a1,value="a")
    aa2 = AgentArseni(a2,value="b")
    aa3 = AgentArseni(a3,value="a")







