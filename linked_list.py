class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None

    def __str__(self):
        return str(self.data)


class LinkedList:
    def __init__(self):
        self.head = None

    def add_last(self, data):
        if not self.head:
            self.head = Node(data)
        else:
            n = self.head
            while n.next != None:
                n = n.next
            n.next = Node(data)

    def find(self, data):
        n = self.head
        if not n:
            return False
        else:
            found = False
            while n != None and not found:
                if n.data == data:
                    found = True
                n = n.next
            return found

    def find_name(self, data):
        n = self.head
        if not n:
            return n.data
        else:
            node_found = None
            found = False
            while n != None and not found:
                if n.data.c_a == data:
                    node_found = n.data
                    found = True
                n = n.next
            return node_found

    def delete(self, data):
        if self.head is None:
            print("Linked list is empty so no element was deleted.")
        else:
            n = self.head
            n_prev = None
            found = False
            while n != None and not found:
                if n.data == data:
                    if n_prev is None:
                        self.head = n.next
                    elif n.next is None:
                        n_prev.next = None
                    else:
                        n_prev.next = n.next
                    found = True
                n_prev = n
                n = n.next

    def print_linked_list(self):
        n = self.head
        if not n:
            print("Linked list is empty.")
        else:
            while n != None:
                print(n.data)
                n = n.next

    def convert_linked_list(self):
        n = self.head
        list = []
        if not n:
            pass
        else:
            while n != None:
                list.append(str(n.data))
                n = n.next
        return list

    def size(self):
        count = 0
        if self.head != None:
            n = self.head
            while n != None:
                count += 1
                n = n.next
        return count

