import csv

def get_values(file_name,pos): #Assuming you want to get some column from this csv file
    val=[]
    with open(file_name, "r") as f:
        for line in f:
            csv_row = line.split() #returns a list ["1","50","60"]
            try:
                l=csv_row[0].split(',')
                #print(l[pos])
                val.append(l[pos])
            except:
                print("Error")
    return val

def edit(file_name,col_pos,values,new_file_name):#values is the list you want to add, col_pos is the position where you wanna add
    counter=0
    fname = new_file_name
    file1 = open(fname, 'a')
    writer = csv.writer(file1)
    with open(file_name, "r") as f:
        for line in f:
            csv_row = line.split() #returns a list ["1","50","60"]
            #print(csv_row)
            try:
                l=csv_row[0].split(',')
                l.insert(col_pos,values[counter])
                fields1=l
                writer.writerow(fields1)
            except:
                print("Could not write")
            counter+=1
    file1.close()

def main():
    v=get_values('test.csv',0)
    edit('test.csv',2,v,'new_csv.csv')

if __name__ == '__main__':
    main()
