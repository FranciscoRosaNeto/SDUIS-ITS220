import tkinter as tk
import pymysql
import datetime
from collections import Counter as count
from tkinter import messagebox


class Database:
    def __init__(self):
        try:
            self.connection = pymysql.connect(host='localhost', user=root, db='store')
        except:
            tk.messagebox.showerror("Error!","Can't write in this file\n %s" % ex)
        else:
            tk.messagebox.Message("Connected successfully")
            self.cur = self.connection.cursor()

class Item:

    def __init__(self, name, price, button):
        self.name = name
        self.price = price
        self.button = button

class Register:

    def __init__(self, parent):
        self.parent = parent
        self.font = ('Calibri', 13)
        parent.title('KIKO`S BBQ RESTAURANT POS SYSTEM')
        self.till = 0
        self.TAX = 0.08
        self.items = {'beef_ribs': Item('Beef Ribs', 4000,
                                        tk.Button(root, text='Beef Ribs',
                                        command=lambda: self.scan('beef_ribs'),
                                        font=self.font)),
                      'pork_ribs': Item('Pork Ribs', 3000,
                                        tk.Button(root, text='Pork Ribs',
                                        command=lambda: self.scan('pork_ribs'),
                                        font= self.font)),
                      'smoked_brisket': Item('Smoked Brisket', 3000,
                                             tk.Button(root, text='Smoked Brisket',
                                             command=lambda: self.scan('smoked_brisket'),
                                             font= self.font)),
                      'pork_belly': Item('Pork Belly', 3500,
                                         tk.Button(root, text='Pork Belly',
                                         command=lambda: self.scan('pork_belly'),
                                         font= self.font)),
                      'grilled_veggies': Item('Grilled Veggies', 2000,
                                              tk.Button(root, text='Grilled Veggies',
                                              command=lambda: self.scan('grilled_veggies'),
                                              font= self.font))}

        self.MAX_NAME_WIDTH = max(map(len, (item.name for item in self.items.values()))) +3
        self.MAX_PRICE_WIDTH = 10
        self.server_label = tk.Label(root, text='Cashier: Mike', font=self.font)
        self.server_label.grid(row=0, column=0, sticky='W')
        self.time_label = tk.Label(root, text='', font=self.font)
        self.time_label.grid(row=0, column=1, columnspan=4, sticky='E')
        for idx,item in enumerate(self.items.values(), start=1):
            item.button.grid(row=idx, column=0, sticky='W')
        self.frame = tk.Frame(root)
        self.frame.grid(row=1, column=1, sticky= 'WE', rowspan=idx+1, columnspan=4)
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.box = tk.Listbox(self.frame,
                              yscrollcommand=self.scrollbar.set,
                              width=self.MAX_NAME_WIDTH + self.MAX_PRICE_WIDTH + 10,
                              font=self.font)
        self.scrollbar.config(command=self.box.yview)
        self.box.grid(row=0, column=1, sticky='NS')
        self.scrollbar.grid(row=0, column=2, sticky='NS')
        self.box.bind("<Double-Button-1>", self.modify_item)
        self.checkout_button = tk.Button(root, text='Checkout', command=self.checkout, font=self.font)
        self.checkout_button.grid(row=idx+2, column=1, sticky='W')
        self.till_button = tk.Button(root, text='Till', command=self.check_till, font=self.font)
        self.till_button.grid(row=idx+2, column=2, sticky='W')
        self.new_order_button = tk.Button(root, text='New Order', command=self.new_order, font=self.font)
        self.new_order_button.grid(row=idx + 2, column=3, sticky='W')
        self.total_label = tk.Label(root, text='', font=self.font)
        self.total_label.grid(row=idx+2, column=4, sticky='E')
        self.new_order()
        self.tick()

    def modify_item(self, event=None):
        top = tk.Toplevel()
        entry = tk.Entry(top, font=self.font)
        entry.pack()
        entry.focus_set()
        def set_new_quantity():
            new_value = int(entry.get())
            idx = self.box.index(tk.ACTIVE)
            self.box.delete(idx)
            code = self.current_codes.pop(idx)
            self.current_order[code] -= 1
            for i in range(new_value):
                self.scan(code)
            top.destroy()
            self.update_totals()
        confirm = tk.Button(top, text='OK', command=set_new_quantity, font=self.font)
        confirm.pack()

    def update_totals(self):
        self.subtotal = sum(self.items[key].price * value for key, value in self.current_order.items())
        self.tax = round(self.subtotal * self.TAX)
        self.total = self.subtotal + self.tax
        self.total_label.config(text=f'{self.format_money(self.subtotal):>25}\n{self.format_money(self.total):>25}')

    def scan(self, code):
        self.current_order[code] += 1
        self.current_codes.append(code) #Append the codes
        name = self.items[code].name
        price = self.format_money(self.items[code].price)
        self.box.insert(tk.END, f'{name:<{self.MAX_NAME_WIDTH}}' + f'{price:>{self.MAX_PRICE_WIDTH + 10}}')
        self.box.see(self.box.size()-1)
        self.update_totals()

    def format_money(self, cents):
        d,c = divmod(cents, 100)
        return f'${d},{c:0>2}'

    def checkout(self):
        self.total_label.config(text=f'TOTAL: {self.format_money(self.total)}\n')
        for item in self.items.values():
            item.button.config(state=tk.DISABLED)
        top = tk.Toplevel()
        label = tk.Label(top, text='Amount paid:')
        label.grid(row=0, column=0)
        text = tk.Entry(top)
        text.grid(row=0, column=1)
        text.focus_set()

        def pay(event=None):
            #tender is integer of pennies
            tender = int(text.get().replace('.',''))
            change = tender - self.total
            label.config(text=f'Change: {self.format_money(change)}. Have a nice day!')
            self.till += self.total
            self.new_order()
            text.config(state=tk.DISABLED)
            go.config(text='Close', command=top.destroy)
        go = tk.Button(top, text='Pay', command=pay)
        go.grid(row=0, column=2)

    def check_till(self, event=None):
        top = tk.Toplevel()
        b = tk.Button(top, text=self.format_money(self.till), command=top.destroy).pack()
        b.pack()
        b.focus_set()

    def new_order(self, event=None):
        self.subtotal = self.tax = self.total = 0
        for item in self.items.values():
            item.button.config(state=tk.NORMAL)
        self.box.delete(0, tk.END)
        self.current_order = count()
        self.current_codes = []
        self.update_totals()

    def tick(self):
        self.time_label.config(text=str(datetime.datetime.now()).rpartition('.')[0])
        self.parent.after(1000, self.tick)

root = tk.Tk()
app = Register(root)
root.mainloop()