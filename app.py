from tkinter import ttk
from tkinter import *
import sqlite3

class Product:
    def __init__(self, root):
        self.window = root
        self.window.title("App Gestor de Produtos") # Window title
        self.window.resizable(1,1) # Activate window redimensions, (0,0) to deactivate
        self.window.wm_iconbitmap('resources/icon.ico')
        #root.geometry("300x200")

        # Create frame
        frame = LabelFrame(self.window, text="Registar um novo Produto", font=('Calibri',16,'bold'))
        frame.grid(row=0,column=0,columnspan=3,pady=20)

        # Create name label
        self.tag_name = Label(frame,text="Nome :",font=('Calibri', 13)) # Text label on frame
        self.tag_name.grid(row=1,column=0) # grid position
        # Name Entry (box that takes name)
        self.name = Entry(frame,font=('Calibri', 13)) # box with text input on frame
        self.name.focus() # mouse focus 
        self.name.grid(row=1,column=1)

        # Create price label
        self.tag_price = Label(frame, text="Preço: ",font=('Calibri', 13)) # text label on frame
        self.tag_price.grid(row=2,column=0)
        # Price Entry (box that takes price)
        self.price = Entry(frame,font=('Calibri', 13)) # box with text input on frame
        self.price.grid(row=2,column=1)

        # Button to add product
        s = ttk.Style()
        s.configure('my.TButton',font=('Calibri',14,'bold'))
        self.add_button = ttk.Button(frame, 
                                     text="Guardar Produto", 
                                     command=self.add_product,
                                     style='my.TButton')
        self.add_button.grid(row=3, columnspan=2, sticky=W+E)

        # Products table
        # personalized style for the table
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11)) # table font
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold')) # header font
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]) # take out borders
        # Table structure
        self.table = ttk.Treeview(height=20,columns=2,style="mystyle.Treeview")
        self.table.grid(row=4,column=0,columnspan=2)
        self.table.heading('#0', text='Nome', anchor=CENTER) # Header 0
        self.table.heading('#1', text='Preço', anchor=CENTER) # Header 1

        # database object creation
        self.db = 'database/products.db' # variable to access database path
        self.get_products() # call to get_products

        # Informative message for user
        self.message = Label(text='', fg='red')
        self.message.grid(row=3,column=0,columnspan=2,sticky=W+E)

        # Delete and edit buttons
        s = ttk.Style()
        s.configure('my.TButton',font=('Calibri',14,'bold'))
        delete_button = ttk.Button(text='ELIMINAR', command=self.del_product, style='my.TButton')
        delete_button.grid(row=5,column=0,sticky=W+E)
        s = ttk.Style()
        s.configure('my.TButton',font=('Calibri',14,'bold'))
        edit_button = ttk.Button(text='EDITAR', command=self.edit_product, style='my.TButton')
        edit_button.grid(row=5,column=1,sticky=W+E)

    def db_query(self, query, params=()):
        with sqlite3.connect(self.db) as con: # Initialize connection
            cursor = con.cursor() # connection cursor to operate database
            result = cursor.execute(query, params) # prepare query wih params, if any
            con.commit() # execute SQL query
        return result
    
    def get_products(self):
        # first clean the table if it has old residual data
        table_records = self.table.get_children() # get table data
        for line in table_records:
            self.table.delete(line)

        # Sql query
        query = 'SELECT * FROM products ORDER BY name DESC'
        db_records = self.db_query(query) # call to db_query method to show results

        # insert new updated data in table
        for line in db_records:
            print(line) # debugging print
            self.table.insert('', 0, text=line[1], values=line[2])
    
    def name_validation(self):
        user_input_name = self.name.get()
        return len(user_input_name) != 0
    
    def price_validation(self):
        user_input_price = self.price.get()
        return len(user_input_price) != 0
    
    def add_product(self):
        if self.price_validation() and self.name_validation():
            query = 'INSERT INTO products VALUES(NULL, ?, ?)' #SQL to insert data (without params)
            params = (self.name.get(), self.price.get()) # SQL query params
            self.db_query(query, params)
            # success message to user
            self.message['text'] = 'Produto {} adicionado com sucesso'.format(self.name.get())
            self.name.delete(0,END) # delete name camp form
            self.price.delete(0,END) # delete price camp form
            #print(self.name.get())
            #print(self.price.get())
        elif self.name_validation() == False and self.price_validation():
            print("O nome é obrigatório.")
            self.message['text'] = "O nome é obrigatório."
        elif self.price_validation() == False and self.name_validation():
            print("O preço é obrigatório")
            self.message['text'] = "O preço é obrigatório"
        else:
            print("O nome e o preço são obrigatórios")
            self.message['text'] = "O nome e o preço são obrigatórios"
        
        self.get_products() # After finished, call this method to update data on the table

    def del_product(self):
        #print(self.table.item(self.table.selection()))
        self.message['text'] = '' # give empty value to message

        # make sure user selects a product
        try:
            self.table.item(self.table.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Por favor, selecione um produto'
            return

        self.message['text'] = ''
        name = self.table.item(self.table.selection())['text']
        query = 'DELETE FROM products WHERE name = ?' # sql query
        self.db_query(query, (name,)) # execute query
        self.message['text'] = 'Produto {} eliminado com sucesso'.format(name)
        self.get_products() # Refresh products table
        return

    def update_products(self, new_name, old_name, new_price, old_price):
        product_modified = False
        query = 'UPDATE products SET name = ?, price = ? WHERE name = ? AND price = ?'
        if new_name != '' and new_price != '':
            # if user updates both price and name
            params = (new_name, new_price, old_name, old_price)
            product_modified = True
        elif new_name != '' and new_price == '':
            # if user updates only the name
            params = (new_name, new_price, old_name, old_price)
            product_modified = True
        elif new_name == '' and new_price != '':
            # if user updates only the price
            params = (new_name, new_price, old_name, old_price)
            product_modified = True

        if (product_modified):
            self.db_query(query, params) # execute query
            self.edit_window.destroy() # close edit window
            self.message['text'] = 'O produto {} foi atualizado com sucesso'.format(old_name) # show message to user
            self.get_products() # refresh products table
        else:
            self.edit_window.destroy() # close edit window
            self.message['text'] = 'O produto {} NÃO foi atualizado'.format(old_name) #show message

    def edit_product(self):
        #print(self.table.item(self.table.selection()))
        self.message['text'] = ''
        try:
            self.table.item(self.table.selection())['text'][0]
        except IndexError as e:
            self.message['text'] = 'Por favor, selecione um produto'
            return
        
        name = self.table.item(self.table.selection())['text']
        price = self.table.item(self.table.selection())['values'][0]

        # Edit products in new window
        self.edit_window = Toplevel() # create a new window to edit
        self.edit_window.title = "Editar Produto"
        self.edit_window.resizable(1,1)
        self.edit_window.wm_iconbitmap('resources/icon.ico')

        title = Label(self.edit_window, text='Edição de Produtos', font=('Calibri',50,'bold'))
        title.grid(column=0,row=0)
        # Frame creation
        frame_edit = LabelFrame(self.edit_window,text='Editar o seguinte Produto', font=('Calibri',16,'bold'))
        frame_edit.grid(row=1,column=0,columnspan=20,pady=20)
        # old name label
        self.old_name_tag = Label(frame_edit, text='Nome antigo: ',font=('Calibri', 13))
        self.old_name_tag.grid(row=2,column=0)
        # entry of old name (text box that can't be modified)
        self.old_name = Entry(frame_edit, 
                              textvariable=StringVar(self.edit_window, value=name), 
                              state='readonly',
                              font=('Calibri', 13))
        self.old_name.grid(row=2,column=1)
        # new name lable
        self.new_name_tag = Label(frame_edit, text='Nome novo: ',font=('Calibri', 13))
        self.new_name_tag.grid(row=3, column=0)
        # entry of new name (text box can be modified)
        self.new_name = Entry(frame_edit)
        self.new_name.grid(row=3,column=1)
        self.old_name.focus() # mouse cursor will go to this entry
        # old price label
        self.old_price_tag = Label(frame_edit, text="Preço antigo: ",font=('Calibri', 13))
        self.old_price_tag.grid(row=4,column=0)
        # entry of old price (text box can't be modified)
        self.old_price = Entry(frame_edit, 
                               textvariable=StringVar(self.edit_window, value=price), 
                               state='readonly',
                               font=('Calibri', 13))
        self.old_price.grid(row=4, column=1)
        # label new price
        self.new_price_tag = Label(frame_edit, text="Preço novo: ",font=('Calibri', 13))
        self.new_price_tag.grid(row=5,column=0)
        # entry new price (text box can be modified)
        self.new_price = Entry(frame_edit,font=('Calibri', 13))
        self.new_price.grid(row=5,column=1)

        # Update products button
        self.update_button = ttk.Button(frame_edit, 
                                        text="Atualizar Produto",
                                        style='my.TButton',
                                        command=lambda:
                                        self.update_products(self.new_name.get(),
                                                             self.old_name.get(),
                                                             self.new_price.get(),
                                                             self.old_price.get()))
        self.update_button.grid(row=6,columnspan=2,sticky=W+E)
        self.new_price_tag.grid(row=5,column=0)
        # entry new price
        self.new_price = Entry(frame_edit,font=('Calibri', 13))
        self.new_price.grid(row=5,column=1)
        '''
        # Update button (REPETIDO)
        self.update_button = ttk.Button(frame_edit, 
                                        text="Atualizar Produto",
                                        command=lambda:
                                        self.update_products(self.new_name.get(),
                                                             self.old_name.get(),
                                                             self.new_price.get(),
                                                             self.old_price.get()))
        self.update_button.grid(row=6,columnspan=2,sticky=W+E)
        '''

if __name__ == '__main__':
    root = Tk() # object of main window
    app = Product(root) # give control of the window to class Product
    root.mainloop() # initiates application cicle, like a while True