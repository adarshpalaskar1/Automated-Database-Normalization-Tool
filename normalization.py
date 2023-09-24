from utils import combinations_string

class database():
    def __init__(self, attr, fd):
        self.attributes = {}

        for i in attr:
            self.attributes[i] = 1

        self.fd = self.functional_dependency(fd)
        self.children_database = {}
        self.prime_attributes = ""
        self.non_prime_attributes = ""
        self.closures = {}
        self.candidate_keys = []
        self.leftchars = self.find_left_chars()
        self.rightChars = "".join(set([i for i in self.attributes if i not in self.leftchars]))
        self.allChars = "".join(sorted(self.attributes))
        self.candidate_keys = self.find_candidate_keys()
        self.find_prime_non_prime()
        self.normal_form, self.errors = self.which_normal_form()
    
    def functional_dependency(self, fd):
        '''
        Converts A->BCD form into A->B, A->C, A->D
        and then stores it in an array
        '''

        fd = [i.replace(' ', '') for i in fd]
        fd = [i.split('->') for i in fd]

        arr_fd = {}

        for i in range(len(fd)):
            fd[i][0] = "".join(sorted(set(fd[i][0])))

        for i in range(len(fd)):
            arr_fd[fd[i][0]] = ""
        
        for each_fd in fd:
            for right in each_fd[1]:
                arr_fd[each_fd[0]]+=right
        
        arr_fd_ = arr_fd.copy()

        for key in arr_fd:
            if key == arr_fd[key]:
                arr_fd_.pop(key)
                continue

            arr_fd_[key] = "".join([i for i in arr_fd_[key] if i not in key])

            arr_fd_[key] = "".join(sorted(set(arr_fd_[key])))
        
        arr_fd = {}

        for key in arr_fd_:
            temp = arr_fd_.copy()
            temp.pop(key)

            closure_key = self.find_closure(key, temp)

            desired = arr_fd_[key]

            if set(desired).issubset(set(closure_key)):
                continue
            else:
                arr_fd[key] = arr_fd_[key]

        return arr_fd
    
    def print_fds(self):
        for key in self.fd:
            print(key, '->', self.fd[key])          
    
    def find_closure(self, attr, fds):
        # if self.closures.get(attr, -1) != -1:
        #     return self.closures[attr]
        
        closure = "".join(set(attr))

        for key in fds:
            if set(key).issubset(set(attr)):
                closure += fds[key]

        closure = "".join(set(closure))

        if closure == attr:
            # self.closures[attr] = closure
            return "".join(sorted(closure))
        
        # self.closures[attr] = closure

        return "".join(sorted(self.find_closure(closure, fds)))
    
    def find_left_chars(self):
        rightChars = ""

        for key in self.fd:
            rightChars += self.fd[key]
        
        rightChars = "".join(set(rightChars))

        leftChars = "".join([i for i in self.attributes if i not in rightChars])

        return leftChars
    
    def find_candidate_keys(self):
        '''
        Finds candidate keys
        '''

        if self.find_closure(self.leftchars, self.fd) == self.allChars:
            return [self.leftchars]
        
        candidate_keys = []

        combos = combinations_string(self.rightChars)

        for combo in combos:
            temp = self.find_closure("".join(sorted(set(self.leftchars + combo))), self.fd)
  
            if temp == self.allChars:
                candidate_keys.append("".join(sorted(set(self.leftchars + combo))))
        
        dic_keys = {}

        for key in candidate_keys:
            dic_keys[key] = 1
        
        candidate_keys_final = []

        for key in candidate_keys:
            if dic_keys[key] == 1:
                candidate_keys_final.append(key)
                for key2 in candidate_keys:
                    if set(key).issubset(set(key2)):
                        dic_keys[key2] = 0
        
        return candidate_keys_final

    def find_prime_non_prime(self):
        chars = ""

        for key in self.candidate_keys:
            for cha in key:
                if cha not in chars:
                    chars+= cha
        
        chars_non = ""
        for char in self.attributes:
            if char not in chars:
                chars_non+=char
        
        chars = "".join(sorted(chars))
        chars_non = "".join(sorted(chars_non))

        self.prime_attributes = chars
        self.non_prime_attributes = chars_non

    def which_normal_form(self):

        '''
        Check for BCNF
        '''
        errors = {}
        flag = -1
        for fd in self.fd:
            flag = 0
            for key in self.candidate_keys:
                if key in fd:
                    flag = 1
                    break
            if flag == 0:
                errors[fd] = self.fd[fd]
            
        
        if len(errors) == 0:
            return "BCNF", errors
        
        '''
        Check for 3NF
        '''

        errors = {}

        flag = -1
        for fd in self.fd:
            flag = 0
            for key in self.candidate_keys:
                if key in fd:
                    flag = 1
                    break
            if flag == 0:
                if self.fd[fd] in self.prime_attributes:
                    flag = 1
            
            if flag == 0:
                errors[fd] = self.fd[fd]
        
        if len(errors) == 0:
            return "3NF", errors

        '''
        Check for 2NF
        '''
        errors = {}
        flag = -1
        for fd in self.fd:
            flag = 1
            if fd not in self.candidate_keys:
                for key in self.candidate_keys:
                    if fd in key:
                        if self.fd[fd] not in self.prime_attributes:
                            flag = 0
                            errors[fd] = self.fd[fd]
        if len(errors) == 0:
            return "2NF", errors
        else:
            errors = {}
            return "1NF", errors

    def subset_fds(self,left):
        combs = combinations_string(left)
        fds_new = {}

        for comb in combs:
            comb = "".join(sorted(set(comb)))
            temp = self.find_closure(comb, self.fd)
            if temp != "":
                fds_new[comb] = temp
                fds_new[comb] = "".join(sorted(set([i for i in fds_new[comb] if i in left])))
                fds_new[comb] = "".join(sorted(set([i for i in fds_new[comb] if i not in comb])))
                if fds_new[comb] == "":
                    fds_new.pop(comb)

        final_fds = []

        for key in fds_new:
            final_fds.append(key +'->' + fds_new[key])

        return final_fds

    def if_2nf(self):
        errors = {}
        flag = -1
        for fd in self.fd:
            flag = 1
            if fd not in self.candidate_keys:
                for key in self.candidate_keys:
                    if fd in key:
                        if self.fd[fd] not in self.prime_attributes:
                            flag = 0
                            errors[fd] = self.fd[fd]
        if len(errors) == 0:
            return "2NF", errors
        else:
            return "1NF", errors
    
    def if_3nf(self):
        errors = {}

        flag = -1
        for fd in self.fd:
            flag = 0
            for key in self.candidate_keys:
                if key in fd:
                    flag = 1
                    break
            if flag == 0:
                if self.fd[fd] in self.prime_attributes:
                    flag = 1
            
            if flag == 0:
                errors[fd] = self.fd[fd]
        
        if len(errors) == 0:
            return "3NF", errors
        else:
            return "Not 3NF", errors

    def if_bcnf(self):
        errors = {}
        flag = -1
        for fd in self.fd:
            flag = 0
            for key in self.candidate_keys:
                if key in fd:
                    flag = 1
                    break
            if flag == 0:
                errors[fd] = self.fd[fd]
            
        
        if len(errors) == 0:
            return "BCNF", errors
        else:
            return "Not BCNF", errors

    def recursive_print_children(self):
        if len(self.children_database) == 0:
            return
        
        print("".join(sorted(set([i for i in self.attributes]))) + " is divided into: ", end = " ")
        for child_database in self.children_database:
            temp = self.children_database[child_database].attributes
            print("".join(sorted(set(temp))), end = ' ')
        print()
        for child_database in self.children_database:
            self.children_database[child_database].recursive_print_children()

    def convert_to_2nf(self, c = 0):
        '''
        Converts to 2NF
        '''
        if c == 0:
            print("[Converting the table to 2NF]")
        self.children_database = {}
        normal_form, errors = self.if_2nf()
        if normal_form == "2NF" and c==0:
            print("[Table already in 2NF]")
            return
        if normal_form == "2NF":
            return
        if c == 0:
            print("[Decomposing into 2NF]")
            print("[Partial Dependencies]")
            for fd in errors:
                print(fd + "->" + errors[fd])

        closures_errors = []

        for key in errors:
            closures_errors.append(self.find_closure(key, self.fd))

        error_chars = "".join(set([i for i in closures_errors]))

        remaining_chars = "".join([i for i in self.attributes if i not in error_chars])

        for key in errors:
            remaining_chars += key
        
        remaining_chars = "".join(sorted(set(remaining_chars)))

        if remaining_chars != "":
            closures_errors.append(remaining_chars)

        fd_errors = {}

        for left in closures_errors:
            fd_errors[left] = self.subset_fds(left)
        
        for key in fd_errors:
            self.children_database[key] = database(key,fd_errors[key])
        
        for key in self.children_database:
            self.children_database[key].convert_to_2nf(c+1)

    def convert_to_3nf(self, c=0):
        '''
        Converts to 3NF
        '''
        # if c == 3:
        #     exit(0)
        if c == 0:
            print("[Converting the table to 3NF]")
        self.children_database = {}
        normal_form, errors = self.if_3nf()
        if normal_form == "3NF" and c == 0:
            print("[Table already in 3NF]")
            return
        if normal_form == "3NF":
            return
        # print("Errors",errors)
        # self.summary()
        # self.print_fds()
        closures_errors = []

        for key in errors:
            closures_errors.append(self.find_closure(key, self.fd))

        error_chars = "".join(set([i for i in closures_errors]))

        remaining_chars = "".join([i for i in self.attributes if i not in error_chars])

        for key in errors:
            remaining_chars += key
        
        remaining_chars = "".join(sorted(set(remaining_chars)))


        if remaining_chars != "":
            closures_errors.append(remaining_chars)
        
        # print("Closure Errors:",closures_errors)
        
        fd_errors = {}

        for left in closures_errors:
            fd_errors[left] = self.subset_fds(left)
        
        # print("FD Errors:",fd_errors)

        for key in fd_errors:
            self.children_database[key] = database(key,fd_errors[key])

        for key in self.children_database:
            self.children_database[key].convert_to_3nf(c+1)

    def convert_to_bcnf(self, c=0):
        '''
        Converts to BCNF
        '''
        if c == 0:
            print("[Converting the table to BCNF]")
        self.children_database = {}
        normal_form, errors = self.if_bcnf()
        if normal_form == "BCNF" and c == 0:
            print("[Table already in BCNF]")
            return
        if normal_form == "BCNF":
            return
        # print("Errors",errors)
        # self.summary()
        # self.print_fds()
        closures_errors = []

        for key in errors:
            closures_errors.append(self.find_closure(key, self.fd))

        error_chars = "".join(set([i for i in closures_errors]))

        remaining_chars = "".join([i for i in self.attributes if i not in error_chars])

        for key in errors:
            remaining_chars += key
        
        remaining_chars = "".join(sorted(set(remaining_chars)))


        if remaining_chars != "":
            closures_errors.append(remaining_chars)
        
        # print("Closure Errors:",closures_errors)
        
        fd_errors = {}

        for left in closures_errors:
            fd_errors[left] = self.subset_fds(left)
        
        # print("FD Errors:",fd_errors)

        for key in fd_errors:
            self.children_database[key] = database(key,fd_errors[key])

        
        # exit(0)
        for key in self.children_database:
            self.children_database[key].convert_to_bcnf(c+1)
  
    def summary(self):
        print()
        print('************* Information about the Database **************')
        print()
        print("Attributes:","".join(sorted(set([i for i in self.attributes]))))
        print('Functional Dependencies')
        self.print_fds()
        print("Candidate Keys:",self.candidate_keys)
        print("Prime Attributes:",self.prime_attributes)
        print("Non-Prime Attributes:",data.non_prime_attributes)
        print("Normal form:",data.which_normal_form()[0])
        print()
        print()

attr = input("Enter the attributes: ")

input_fd = input("Enter the functional dependencies: ")
input_fd = input_fd.split(',')

data = database(attr, input_fd)

data.summary()

form = input("Enter the normal form to convert to: ")

if form == "2NF":
    data.convert_to_2nf()
elif form == "3NF":
    data.convert_to_3nf()
elif form == "BCNF":
    data.convert_to_bcnf()

data.recursive_print_children()