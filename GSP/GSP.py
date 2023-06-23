import pandas as pd


class GSP:
    def __init__(self, min_sup, path):
        self.freq_Item_List = []
        self.min_sup = min_sup
        self.path = path

        self.Customer_seq_stuff = self.parse_data()

        self.One_Item_List = self.one_item_lst(self.Customer_seq_stuff)
        self.freq_Item_List.append(self.One_Item_List)

        self.Two_Item_List = self.two_item_lst(self.One_Item_List, self.Customer_seq_stuff)
        self.freq_Item_List.append(self.Two_Item_List)

        while True:
            self.n_Item_List = self.n_item_lst(self.freq_Item_List[-1], self.Customer_seq_stuff)
            if self.n_Item_List[1] is True:
                break
            self.freq_Item_List.append(self.n_Item_List[0])

        # Frequent item list
        print(self.freq_Item_List)

    def parse_data(self):
        Customer_seq_stuff = {}
        lst = []
        df = pd.read_excel(self.path)
        customerID = df['Customer ID'].tolist()
        Items = df['Item Purchased'].tolist()
        # print(Items)
        # Creating Sequence table
        for x in range(len(Items)):
            lst1 = [customerID[x], Items[x]]
            lst.append(lst1)
        # print(lst)
        for i in range(len(lst)):
            if lst[i][0] in Customer_seq_stuff.keys():
                Customer_seq_stuff[lst[i][0]].append(lst[i][1])
            else:
                Customer_seq_stuff[lst[i][0]] = []
                Customer_seq_stuff[lst[i][0]].append(lst[i][1])
        # print(Customer_seq_stuff)
        return Customer_seq_stuff

    def one_item_lst(self, Customer_seq_stuff):
        One_Item_Dic = {}
        One_Item_List = []
        One_Items_sup = [0] * 26
        # Calculating every element's support
        for item_dic in Customer_seq_stuff:
            _set = set()
            for item in Customer_seq_stuff[item_dic]:
                if len(item) == 1:
                    if item not in _set:
                        One_Items_sup[ord(item) - 65] = One_Items_sup[ord(item) - 65] + 1
                        _set.add(item)
                else:
                    for itm in item:
                        if itm not in _set:
                            One_Items_sup[ord(itm) - 65] = One_Items_sup[ord(itm) - 65] + 1
                            _set.add(itm)
        # one Item Support
        # print(One_Items_sup)
        # eliminating under-min-support elements
        for i in range(len(One_Items_sup)):
            if One_Items_sup[i] < self.min_sup:
                One_Items_sup[i] = 0
        # print(One_Items_sup)
        # Getting One_Item_List
        for i in range(len(One_Items_sup)):
            if One_Items_sup[i] != 0:
                One_Item_List.append(chr(65 + i))
        # print(One_Item_List)
        # Candidate of 1-item sequence
        j = 0
        for i in range(len(One_Item_List)):
            while One_Items_sup[j] == 0:
                j = j + 1
            One_Item_Dic[One_Item_List[i]] = []
            One_Item_Dic[One_Item_List[i]] = One_Items_sup[j]
            j = j + 1
        # print(One_Item_Dic)
        return One_Item_List

    def two_item_lst(self, One_Item_List, Customer_seq_stuff):
        # print(Customer_seq_stuff)
        one_len = len(One_Item_List)
        temporal = [[0 for _ in range(one_len)] for _ in range(one_len)]
        non_temporal = [[0 for _ in range(one_len)] for _ in range(one_len)]

        # All Possible temporal, non-temporal Joins
        for i in range(one_len):
            for j in range(one_len):
                temporal[i][j] = One_Item_List[i] + ',' + One_Item_List[j]
                if i < j:
                    non_temporal[i][j] = One_Item_List[i] + One_Item_List[j]
        # print(temporal)
        # print(non_temporal)

        # Getting all candidates
        two_item_candidates = []
        for i in range(one_len):
            for j in range(one_len):
                two_item_candidates.append(temporal[i][j])
        for i in range(one_len):
            for j in range(one_len):
                if i < j and non_temporal[i][j] != 0:
                    two_item_candidates.append(non_temporal[i][j])
        # print(two_item_candidates)

        # assigning support
        Two_Item_Dic = self.count_support(two_item_candidates, Customer_seq_stuff)
        # print(Two_Item_Dic)

        # eliminating items with support less than 2
        Two_Item_List = self.frequentItemsList(Two_Item_Dic)
        # print(Last_Item_List)

        return Two_Item_List

    def n_item_lst(self, Last_Item_List, Customer_seq_stuff):
        # print(Customer_seq_stuff)
        # print(Last_Item_List)
        Last_item_join = []
        no_more_combination = True
        for i in range(len(Last_Item_List)):
            for j in range(len(Last_Item_List)):
                if i != j:
                    joined_item = self.join_item(str(Last_Item_List[i]), str(Last_Item_List[j]), no_more_combination)
                    if joined_item[0] != "":
                        Last_item_join.append(joined_item[0])
                    if joined_item[1] is False:
                        no_more_combination = False
        # print(Last_item_join)
        Last_Item_Dic = self.count_support(Last_item_join, Customer_seq_stuff)
        # print(Last_Item_Dic)
        Last_Item_List = self.frequentItemsList(Last_Item_Dic)
        # print(Last_Item_List)
        return Last_Item_List, no_more_combination

# HELPER FUNCTIONS
    # join more than 2 items
    @staticmethod
    def join_item(item1, item2, no_more_combination):
        joined_item = ""
        for i in range(len(item1)):
            if item2.startswith(item1[i:]):
                joined_item = item1 + item2[len(item1[i:]):]
                no_more_combination = False
        return joined_item, no_more_combination

    # check if element in sequence
    @staticmethod
    def check_subseq(lst, seq):
        temp_lst = []
        j = 0
        for i in range(len(seq)):
            if seq[i].__contains__(lst[j]):
                temp_lst.append(lst[j])
                j = j + 1
            if temp_lst == lst:
                return temp_lst == lst
        return temp_lst == lst

    # counting support
    def count_support(self, candidates, Customer_seq_stuff):
        dic = {}
        for item in candidates:
            lst = item.split(',')
            for seq in Customer_seq_stuff.values():
                if self.check_subseq(lst, seq):
                    if item in dic.keys():
                        dic[item] = dic[item] + 1
                    else:
                        dic[item] = []
                        dic[item] = 1
        return dic

    # Getting all frequent items
    def frequentItemsList(self, Two_Item_Dic):
        remove_it = []
        Item_List = []
        for item in Two_Item_Dic:
            if Two_Item_Dic[item] < self.min_sup:
                remove_it.append(item)
        for item in range(len(remove_it)):
            Two_Item_Dic.pop(remove_it[item])

        for item in Two_Item_Dic:
            Item_List.append(item)
        return Item_List
