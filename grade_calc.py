#%%
import csv
#it became a gradebook
#I want to make this a data structure too...
"""
Gradebook
- main gradebook ds (GUI)
    - weakest subject
    - calculate grades for each subj
    - insert units
    - update any grade in the units
    - view summary of all subjects
- grade node
    - weightage, marks, name, total
    - add feedback ?
    - add_topic ? 
- grade heap
    - insert
    - update
    - current grade
    - weakest topic (based on assesment lowest percentage)
- grades enum (idk if i rly need this now)
"""


#%% Grade Tree
import enum
class Grades(enum.Enum):
    HD = 80
    D = 70
    C = 60
    P = 50
    N = 0

    def match_grade(percentage):
        # might just return the 'HD' 
        if percentage > Grades.HD.value:
            return Grades.HD
        elif percentage > Grades.D.value:
            return Grades.D
        elif percentage > Grades.C.value:
            return Grades.C
        elif percentage > Grades.P.value:
            return Grades.P
        else:
            return Grades.N



#%% GradeHeap
class GradeNode:
    #if you want to add feedback etc 
    # I will add a topic section?
    # that was connascenece of order <- not good
    def __init__(self, key, mark, max_score, weight):
        self.assesment = key
        self.mark = mark
        self.max_score = max_score
        self.weightage = weight
        self.perc = (mark/max(1,self.max_score))*100
        self.grade = Grades.match_grade(self.perc)
        self.feedback = None
        self.topic = None
    
    def add_feedback(self, desc: str):
        self.feedback = desc

    def assign_topic(self, topic):
        self.topic = topic

    def __str__(self):
        return '{}--{}--{}--{}'.format(self.assesment, self.mark, self.max_score, self.weightage)

class GradeHeap:
    def __init__(self, subj, perc):
        self.subject = subj
        self.max_perc = perc
        self.array = [0] #first one will be used as total internal score
        self.size = 0
    
    def insert(self, assesment, marks, max_pos, weight):
        node = GradeNode(assesment, marks, max_pos, weight)
        self.array.append(node)
        self.array[0] += (node.perc*0.01) * node.weightage #get the actual marks
        self.size += 1
        self.rise(self.size)
    
    def getMin(self):
        #I should edit this to make it just show? or i could reinsert
        print(self.size)
        self.array[-1], self.array[1] = self.array[1], self.array[-1]
        self.size -= 1
        ret_node = self.array.pop()
        self.array[0] -= ret_node.perc * ret_node.weightage
        return ret_node

    def rise(self, i):
        parent = i//2
        while parent > 0:
            if self.array[parent].perc > self.array[i].perc:
                self.array[parent], self.array[i] = self.array[i], self.array[parent]
                i = parent
                parent = parent//2
            else:
                break

    def sink(self, i):
        child = 2*i
        while child <= self.size:
            if child + 1 < self.size and self.array[child + 1].perc > self.array[child].perc:
                child += 1
            if self.array[i].perc > self.array[child].perc:
                self.array[i], self.array[child] = self.array[child], self.array[i]
                i = child
                child = 2*i
            else:
                break

    def update(self,key, marks, p_mark, weightage):
        for i in range(1, len(self.array)):
            cur = self.array[i]
            elem = cur.assesment
            if p_mark == 0:
                p_mark = cur.max_score
            if weightage == 0:
                weightage = cur.weightage
            score = (cur.perc * 0.01) * weightage
            if elem == key:
                node = GradeNode(key, marks, p_mark, weightage)
                self.array[i] = node
                self.array[0] -= score
                self.array[0] += (node.perc * 0.01) * weightage
    
    def all_marks(self):
        # this is a heapsort
        temp_arr = [self.array[0]]
        while self.size >= 1:
            node = self.getMin()
            temp_arr.append(node)
            print(node.assesment, node.perc, node.mark, node.grade)
        self.array = temp_arr
        self.size = len(self.array)-1
    
    def get_score(self):
        return self.array[0]
    
    def __str__(self):
        #terrible time complexity
        ret = ''
        for i in range(1, len(self.array)):
            ret += str(self.array[i])
            if i != self.size:
                ret += '\n'
        return ret


# gh = GradeHeap('unit', 50)
# gh.insert('a1', 25, 50, 10)
# gh.insert('a2',45, 50, 10)
# gh.insert('a3', 10, 10, 10)
# gh.all_marks()
# gh.update('a1', 47)
# gh.all_marks()


# %%

# %%
import csv
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox

def split_test(desc):
    ret = desc.split('--')
    return ret[0], float(ret[1]), int(ret[2]), int(ret[3])

def makeTree(filename = 'gradebook.csv'):
    units = []
    names = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) > 0: # there's buffer rows between
                subject = row[0]
                total = row[1]
                gh = GradeHeap(subject, total)
                for i in range(2, len(row)):
                    grade = row[i]
                    test, mark, max_score, weightage = split_test(grade)
                    gh.insert(test, mark, max_score, weightage)
                units.append(gh)
    for unit in units:
        names.append(unit.subject)
    csv_file.close()
    return names, units

def saveTree(units,filename = 'gradebook.csv'):
    with open(filename, mode='w') as gradebook:
        grade_writer = csv.writer(gradebook, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for unit in units:
            lst = [unit.subject, unit.max_perc]
            for i in range(1,len(unit.array)):
                lst.append(str(unit.array[i]))
            grade_writer.writerow(lst)
    gradebook.close()

class unitWindow:
    DATA=("one", "two", "three", "four")
    def __init__(self, win, units, subject):
        self.chooseAss = Label(win, text = "Choose Assesment")
        self.marks = Label(win, text = "Mark Acquired")
        self.btn2=Button(win, text='Add Grade', command = self.addGrade)
        self.btn2.place(x=100, y=115)
        self.chooseAss.place(x=10, y=20)
        data=("one", "two", "three", "four")
        self.cb2=Combobox(win, values=data)
        self.cb2.place(x=120, y=20)
        self.marks.place(x=10, y= 80)
        self.t1=Entry(win, bd=3)
        self.t1.place(x=120, y= 80)
        self.currentGrade = Label(win, text = "Current grade")
        self.currentGrade.place(x = 10, y = 50)
        score = 'None' #get from units
        self.score = Label(win, text = score)
        self.score.place(x = 120, y =50 )
    
    def addGrade(self):
        test = self.cb2.get()
        num=int(self.t1.get())
        print(test, num)

class addWindow:
    def __init__(self, win, units, names):
        self.win = win
        self.names = names
        self.addUnit = Label(win, text="Unit")
        self.newUnit = Entry(win, bd=2)
        self.newUnit.place(x=80, y=10)
        self.addUnit.place(x=10, y=10)
        self.addButton = Button(win, text = 'Add Unit', command = self.add_new_unit)
        self.addButton.place(x=80, y=65)
        self.unit_perc = Label(win, text = "Weightage")
        self.unit_perc.place(x = 10, y = 40)
        self.enter_weight = Entry(win, bd = 2)
        self.enter_weight.place(x = 80, y = 40)
        self.units = units
        self.unitbox = Combobox(win,values = self.names)
        self.delete_unit = Button(win, text = "Delete Unit", command = self.deleteUnit)
        self.unitbox.place(x=95, y = 100)
        self.delete_unit.place(x=95, y = 130)
        self.delete_label = Label(win, text = "Unit to Delete")
        self.delete_label.place(x = 10, y = 100)
        # self.edit_info = Label(win, text = "Edit Unit Info")
        # self.edit_info.place( x=10, y = 60)
    
    def editUnit(self, name):
        for unit in self.units:
            if unit.subject == name:
                pass 
    
    #DONE
    def add_new_unit(self):
        if len(self.newUnit.get()) != 0:
            if len(self.enter_weight.get()) != 0:
                unit = GradeHeap(self.newUnit.get(), self.enter_weight.get())
                self.units.append(unit)
                messagebox.showinfo("Success", unit.subject + " was added")
                self.win.destroy()
            else:
                messagebox.showerror("Title", "No Weightage Provided!")
        else:
            messagebox.showerror("No Unit", "No Unit Entered!")

    def deleteUnit(self):
        i = 0
        subject = self.unitbox.get()
        while i < len(self.units):
            if self.units[i].subject == subject:
                break
            i += 1
        if i < len(self.units):
            messagebox.showinfo("Success", self.names[i] + " was succesfully deleted!")
            self.units.pop(i)
            self.win.destroy()
    
    def close_n_return(self):
        self.win.destroy()
        return self.units
    
class addTestMenu:
    def __init__(self, win, units, unit):
        self.units = units
        self.unit = unit
        self.window = win
        self.add_button = Button(win, text = "Add", command = self.add_assesment)
        self.edit_button = Button(win, text = "Edit", command = self.edit_assesment)
        self.test_name = Label(win, text = "Name")
        self.test_marks = Label(win, text = "Marks Available")
        self.test_marks_o = Label(win, text = "Marks Obtained")
        self.test_weight = Label(win, text = "Weightage")
        self.test_name.place(x = 10, y = 10)
        self.test_marks.place(x= 10, y = 35)
        self.test_marks_o.place(x = 10, y = 55)
        self.test_weight.place(x = 10, y = 75)
        self.name = Entry(win, bd=2)
        self.marks = Entry(win)
        self.marks_o = Entry(win)
        self.weight = Entry(win)
        self.name.place(x = 110, y= 10)
        self.marks.place(x = 110, y = 35)
        self.marks_o.place(x = 110, y = 55)
        self.weight.place(x = 110 ,y = 75)
        self.add_button.place(x = 30, y = 95)
        self.edit_button.place(x = 120, y = 95)
        win.protocol('WM_DELETE_WINDOW', self.close_window)
    
    def add_assesment(self):
        for unit in self.units:
            if unit.subject == self.unit:
                name = self.name.get()
                gotten = int(self.marks_o.get())
                possible = int(self.marks.get())
                weight = int(self.weight.get())
                unit.insert(name, gotten, possible, weight)
                messagebox.showinfo("Success", "Assesment Added")
    
    def edit_assesment(self):
        for unit in self.units:
            if unit.subject == self.unit:
                name = self.name.get()
                gotten = int(0 if self.marks_o.get() == '' else self.marks_o.get())
                possible = int(0 if self.marks.get() == '' else self.marks.get())
                weight = int(0 if self.weight.get() == '' else self.weight.get())
                unit.update(name, gotten, possible, weight)
                messagebox.showinfo("Success", "Assesment Edited")

    def close_window(self):
        self.window.destroy()
        return self.units

class mainMenu:
    def __init__(self, win):
        self.window = win
        self.unitButton = Button( win, text = 'Edit/Add Unit', command = self.addUnit)
        self.gradesButton = Button(win, text = 'Add Grades', command = self.addGrade)
        self.unitButton.place(x=110, y = 10)
        self.gradesButton.place(x=10, y =80)
        #['FIT2014', 'FIT2086', 'FIT1055', 'FIT3080']
        self.data, self.all_units = makeTree()
        self.units = Combobox(win, values=self.data)
        self.units.place(x = 110, y = 45)
        self.menu = Label(win, text = 'Edit unit info')
        self.menu.place(x=10,y=10)
        self.unitLabel = Label(win, text = 'Choose a Unit')
        self.unitLabel.place(x = 10, y = 45)
        self.weak = Button(win, text = 'Weakest Topic', command = self.weakTopic)
        self.weak.place(x = 150, y = 120)
        self.scorePlan = Button(win, text = 'Marks required', command = self.marksReq)
        self.scorePlan.place(x = 50, y = 120)
        self.add_test = Button(win, text = "Add Assesment", command = self.add_assesment)
        self.add_test.place(x = 90, y = 80)
        self.exit_window = Button(win, text = "Exit", command = self.end_this)
        self.exit_window.place(x = 10, y = 120)
        self.edit_test = Button(win, text = "Edit Assesment", command = self.add_assesment)
        self.edit_test.place(x = 200, y = 80)
        win.protocol('WM_DELETE_WINDOW', self.close_window)
    
    def end_this(self):
        self.window.destroy()

    def addUnit(self):
        uWdow = Tk()
        myUnit = addWindow(uWdow, self.all_units, self.data)
        uWdow.title('Add Unit')
        uWdow.geometry("280x180")
        uWdow.mainloop()
    
    def addGrade(self):
        wdow=Tk()
        mywin=unitWindow(wdow,self.all_units, self.units.get())
        wdow.title('Add Grade')
        wdow.geometry("280x150")
        wdow.mainloop()
    
    def add_assesment(self):
        window = Tk()
        new_units = addTestMenu(window, self.all_units, self.units.get())
        window.title("Add Assesment")
        window.geometry("250x130")
        window.mainloop()
        self.all_units = new_units
    
    def weakTopic(self):
        pass

    def marksReq(self):
        unit = self.units.get()
        for u in self.all_units:
            if u.subject == unit:
                print(u.get_score(), u.max_perc)

    def edit_assesment(self):
        pass

    def close_window(self):
        for unit in self.all_units:
            print(unit.subject + "\nAssesments")
            print(str(unit) + "\n")
        saveTree(self.all_units)
        self.window.destroy()

class MyWindow:
    def __init__(self, win):
        self.lbl1=Label(win, text='First number')
        self.lbl2=Label(win, text='Second number')
        self.lbl3=Label(win, text='Result')

    def add(self):
        self.t3.delete(0, 'end')
        num1=int(self.t1.get())
        num2=int(self.t2.get())
        result=num1+num2
        self.t3.insert(END, str(result))
    def sub(self, event):
        self.t3.delete(0, 'end')
        num1=int(self.t1.get())
        num2=int(self.t2.get())
        result=num1-num2
        self.t3.insert(END, str(result))


addWdow = Tk()
myAdd = mainMenu(addWdow)
addWdow.title('Menu')
addWdow.geometry("300x160")
addWdow.mainloop()

# window=Tk()
# mywin=MyWindow(window)
# window.title('Calculator')
# window.geometry("400x330")
# window.mainloop()
    
# %%
ok = 'hello'
bye = "hi"
string = ok + "\n\n" + bye
print(string)
# %%
