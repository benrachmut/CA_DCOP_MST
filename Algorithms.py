from Entities import AgentAlgorithm


class DSA (AgentAlgorithm):
    def initiate_algorithm(self):
        """
        before thread starts the action in this method will occur
        :return:
        """

    def measurements_per_agent(self):
        """
        NotImplementedError
        :return: dict with key: str of measure, value: the calculated measure
        """

    # ---------------------- receive_msgs ----------------------


    def set_receive_flag_to_true_given_msg(self, msg):

        """
        given msgs received is agent going to compute in this iteration?
        set the relevant computation flag
        :param msg:
        :return:
        """


    def get_current_timestamp_from_context(self, msg):

        """
        :param msg: use it to extract the current timestamp from the receiver
        :return: the timestamp from the msg
        """


    def update_message_in_context(self, msg):

        '''
        :param msg: msg to update in agents memory
        :return:
        '''


    # ---------------------- receive_msgs ----------------------



    # ---------------------- reaction_to_msgs ----------------------


    def get_is_going_to_compute_flag(self):
        """
        :return: the flag which determines if computation is going to occur
        """

    def compute(self):
        """
       After the context was updated by messages received, computation takes place
       using the new information and preparation on context to be sent takes place
        """



    def get_list_of_msgs_to_send(self):
        """
        create and return list of msgs to send
        """

    def set_receive_flag_to_false(self):
        """
        after computation occurs set the flag back to false
        :return:
        """

    def reset_additional_fields(self):


class DSA_ASY:
    pass

class DSA_SY:
    pass