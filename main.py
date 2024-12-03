from typing import Tuple
import customtkinter as ct
from tkinter import *
from math import *
from gtts import gTTS
import pygame

class interface(ct.CTk):

    n = 180
    circle_r = 20

    def __init__(self, fg_color: str | Tuple[str, str] | None = None, **kwargs):
        super().__init__(fg_color, **kwargs)

        self.geometry('740x620')

        self.nodes = []
        self.edges = {}
        self.canvas_entity = []
        self.nodes_coords = {}
        self.graph_type = None
        self.edges_passed = []
        self.weight = {}
        self.set_weight = False

        top_frame = ct.CTkFrame(self)
        self.canvas = Canvas(self, height = 480, width= 720)

        top_frame.grid(row = 0, column = 0, padx = 10, pady = 10)


        add_node = ct.CTkButton(top_frame, text = "créer un graph", command = lambda : self.open_graph_wd())
        del_node = ct.CTkButton(top_frame, text = "modifier le graph", command = lambda : self.open_graph_wd(self.nodes, self.edges))
        
        add_node.grid(row = 0, column = 0, padx = 10, pady = 10)
        del_node.grid(row = 0, column = 1, padx = 10, pady = 10)

        
        self.canvas.grid(row = 1, column = 0, padx = 10, pady = 10)



    def open_graph_wd(self, nodes : list = None, edges : dict = None):
        wd = CreateGraph(nodes = nodes, edges = edges)
        data = wd.return_data()
        self.nodes, self.edges, self.graph_type, self.weight = data[0], data[1], data[2], data[3]
        if self.weight != {} :
            self.set_weight = True
        print(self.graph_type)
        self.clear_canvas()
        if len(self.nodes) > 0 :
            self.create_graph(len(self.nodes))


    def clear_canvas(self):
        for i in range(len(self.edges_passed)):
            self.canvas.delete(i)
        for element in self.canvas_entity :
            if type(element) == tuple :
                self.canvas.delete(element[0])
                element[1].destroy()
            else : 
                element.destroy()
        self.canvas_entity = []
    

    def create_graph(self, nodes_nb : int):
        coords : list = self._get_coords(nodes_nb)
        print(self.nodes)
        for i in range(nodes_nb):
            self.nodes_coords[self.nodes[i]] = coords[i]
        self.create_edge()
        for i in range(len(coords)):
            obj = self.canvas.create_oval(coords[i][0]-self.circle_r, 
                                  coords[i][1]-self.circle_r, 
                                  coords[i][0]+self.circle_r, 
                                  coords[i][1] + self.circle_r, fill = "blue", tags = 'test')
            lbl = ct.CTkLabel(self.canvas, text = self.nodes[i], bg_color = "blue", text_color= "#FFFFFF", font = ct.CTkFont(family="Arial", size = 15))
            lbl.place(x = coords[i][0]-5, y = coords[i][1]-12)
            self.canvas_entity.append((obj, lbl))
            

    def create_edge(self):
        print(self.graph_type)
        for origin, dest in self.edges.items() :
            for point in dest :
                
                if set((origin, point)) not in self.edges_passed and origin != point:
                    coords, arc_deg = self._get_edge_coords(self.nodes_coords[origin], self.nodes_coords[point])
                    
                    
                    if self.set_weight :
                        self._create_weight(x1 = coords[0],  y1 = coords[1], x2 = coords[2], y2 =coords[3], 
                                            weight = self.weight[(point, origin)] if (point, origin) in self.weight.keys() else self.weight[(origin, point)],
                                            adj= arc_deg)
                    
                    
                    if self.graph_type == "orienté" :
                        print("arrow : ",coords, "origin :", self.nodes_coords[origin], "end : ", self.nodes_coords[point]) 
                        if origin in self.edges[point] :
                            arrow_look = "both"
                        else : 
                            arrow_look = "last"
                        obj = self.canvas.create_line(coords[0], 
                                                coords[1], 
                                                coords[2], 
                                                coords[3], 
                                                arrow = arrow_look)
                        self.edges_passed.append(set((origin, point)))
                    else : 
                        self.canvas.create_line(coords[0], 
                                                coords[1], 
                                                coords[2], 
                                                coords[3])
                        self.edges_passed.append(set((origin, point)))
                    
    
    def _get_edge_coords(self, n1 : Tuple, n2 : Tuple) :

        def _triangulation():
            adj : int = abs(n2[0] - n1[0])
            opp : int = abs(n2[1] - n1[1])
            hyp : int = int(sqrt(adj**2 + opp**2))
            return adj,hyp
    
        def _get_cos(adj,hyp):
            cos1 : float = acos(adj/hyp)
            cos2 : float = asin(adj/hyp)

            xless1 : int = int(self.circle_r*cos(cos1))
            yless1 : int =  int(self.circle_r*sin(cos1))
            xless2 : int = int(self.circle_r*sin(cos2))
            yless2 : int = int(self.circle_r*cos(cos2))
        
            return xless1, yless1, xless2, yless2, cos1
        
        def _get_coords(xless1, yless1, xless2, yless2):
            if n2[0] - n1[0] < 0 :
                x1, x2 = n1[0] - xless1, n2[0] + xless2
            else : 
                x1, x2 = n1[0] + xless1, n2[0] - xless2

            if n2[1] - n1[1] < 0 :
                y1, y2 = n1[1] - yless1, n2[1] + yless2
            else : 
                y1, y2 = n1[1] + yless1, n2[1] - yless2
            return x1, y1, x2, y2


        adj,hyp =  _triangulation()
        xless1, yless1, xless2, yless2, cos1 = _get_cos(adj, hyp)
        x1, y1, x2, y2 = _get_coords(xless1, yless1, xless2, yless2)

        return (x1,y1,x2,y2), cos1


    def _get_coords(self, n : int) -> list:
        arc : float = 360/n
        const_arc : float = arc
        nodes_loc : list = [(int(self.canvas.cget("width"))/2 + self.n, int(self.canvas.cget("height"))/2 )]

        for i in range(n-1):
            rad_arc : float = (arc*pi)/180

            x : int = int(self.n*cos(rad_arc))
            y : int = int(self.n*sin(rad_arc))
            print(arc)
            print(f"y{i} : ", y)
            print(f"x{i} : ", x)
            nodes_loc.append((x + int(self.canvas.cget("width"))/2,
                              y + int(self.canvas.cget("height"))/2, i+1)
                              )
            arc += const_arc
        
        return nodes_loc
    

    def _create_weight(self, **kwargs):
        x : int = int((kwargs["x2"]- kwargs["x1"])/2)
        y : int = int((kwargs["y2"]- kwargs["y1"])/2)

        x += sin(kwargs["adj"])*15
        y += cos(kwargs["adj"])*15
        print(cos(kwargs["adj"])*15, kwargs["weight"])

        x += kwargs["x1"]
        y += kwargs["y1"]
        print(x, y)
        lbl : object = ct.CTkLabel(self.canvas, text = kwargs["weight"], text_color= "#000000")
        lbl.place(x = x, y = y)
        self.canvas_entity.append(lbl)

    




class CreateGraph(ct.CTkToplevel):

    def __init__(self, **kwargs):
        super().__init__()

        self.grab_set()

        self.nodes = [] if kwargs["nodes"] == None else kwargs["nodes"]
        self.edges = {} if kwargs["edges"] == None else kwargs["edges"]
        self.weight_dict = {}

        add_node = ct.CTkButton(self, text = "ajouter des noeuds", command = lambda : self._add_nodes())
        self.add_edge = ct.CTkButton(self, text = "ajouter des arrêtes", command = lambda : self._add_edges())
        if self.nodes == []:
            self.add_edge.configure(state = "disabled")
        confirm_bt = ct.CTkButton(self, text = "confirmer", command = lambda : self.confirmed())
        self.type_var = None
        self.graph_type = ct.CTkSegmentedButton(self, values= ["orienté", "non-orienté"], variable= self.type_var)
        self.weight_var = None
        self.weight = ct.CTkSegmentedButton(self, values= ["non-pondéré", "pondéré"], variable= self.weight_var, command = lambda x : self._weight_callback())
        self.weight_bt = ct.CTkButton(self, text = "pondérations", command = lambda : self._weight_wd())

        
        add_node.grid(row = 0, column = 0, padx = 10, pady = 10, columnspan = 2)
        self.add_edge.grid(row = 1, column = 0, padx = 10, pady = 10, columnspan = 2)
        self.graph_type.grid(row = 2, column = 0, padx = 10, pady = 10, columnspan = 2)
        confirm_bt.grid(row = 4, column = 0, padx = 10, pady = 10, columnspan = 2)
        self.weight.grid(row = 3, column = 0, padx = 10, pady = 10)
        self.weight_bt.grid(row = 3, column = 1, padx = 10, pady = 10)


    def confirmed(self):
        if self.type_var not in ["orienté", "non-orienté"] :  
            self.type_var = "non-orienté"
        self.destroy()

    
    def _weight_callback(self):
        pass

    
    def _weight_wd(self):
        toplevel = WeightTopLevel(self.edges, self.graph_type.get())
        self.weight_dict = toplevel.contentGet()
        

    def _add_nodes(self):
        toplevel = NodesTopLevelWin(self.nodes)
        self.nodes = toplevel.contentGet() 
        if self.nodes != [] :
            self.add_edge.configure(state = "normal")


    def _add_edges(self):
        toplevel = EdgesTopLevelWin(self.nodes)
        self.edges = toplevel.return_value()


    def return_data(self):
        self.wait_window()
        return (self.nodes, self.edges, self.graph_type.get(), self.weight_dict)



class WeightTopLevel(ct.CTkToplevel):

    def __init__(self, nodes : dict, graph_type : str, weight : dict = None):
        super().__init__()


        self.nodes_list = []
        self.max_row = 0
        self.return_values = {}
        self.entries = []

        print(graph_type, graph_type == "orienté")
        if graph_type == "orienté":
            for origin, dest in nodes.items():
                for point in dest :
                    self.nodes_list.append((origin, point))
        else :
            for origin, dest in nodes.items():
                for point in dest :
                    if set((origin, point)) not in self.nodes_list:
                        self.nodes_list.append(set((origin, point)))

        self.validate_bt = ct.CTkButton(self, text = "valider", font= ct.CTkFont(family = "arial", size=15), width= 65, command = lambda : self.contentValidation())
        self.cancel_bt = ct.CTkButton(self, text = "annuler", font= ct.CTkFont(family = "arial", size=15), width= 65, command = lambda : self.on_quit())


        if len(self.nodes_list) > 0 :
            for i in range(len(self.nodes_list)):
                lbl = ct.CTkLabel(self, text = self.nodes_list[i])
                entry = ct.CTkEntry(self, height= 30, width=200, font= ct.CTkFont(family = "arial", size=15))

                self.entries.append((entry, lbl, self.nodes_list[i] ))
                lbl.grid(column =0, row = i, padx = 5, pady = 5)
                entry.grid(column =1, row = i, padx = 5, pady = 5)
                self.max_row +=1

        self.validate_bt.grid(row = self.max_row, column =0, padx = 5, pady = 5)
        self.cancel_bt.grid(row = self.max_row, column =1, padx = 5, pady = 5)

    
    def on_quit(self, event):
        self.destroy()

 
    def contentValidation(self):
        print(self.entries)
        for entry in self.entries :
            val =entry[0].get()
            if val != "" :
                self.return_values[entry[2]] = val
            else :  
                self.return_values[entry[2]] = 0
        self.destroy()


    def contentGet(self):
        self.wait_window()
        return self.return_values


        

class EdgesTopLevelWin(ct.CTkToplevel):

    
    def __init__(self, nodes):
        super().__init__()

        self.nodes = nodes
        self.grab_set()
        row = 0
        col = 1
        for i in range(len(nodes)):
            lbl = ct.CTkLabel(self, text = nodes[i])
            lbl.grid(row = row, column = col, padx = 10, pady = 10, sticky = "w")
            col +=1
        under_col = 0
        row = 1
        self.cb_list = []
        for i in range(len(nodes)):
            lbl = ct.CTkLabel(self, text = nodes[i])
            lbl.grid(row = row, column = under_col, padx = 10, pady = 10)
            liste = []
            for y in range(len(nodes)):
                under_col +=1
                lbl = ct.CTkCheckBox(self, text = "")
                lbl.grid(row = row, column = under_col, padx = 10, pady = 10)
                liste.append(lbl)
            self.cb_list.append(liste)
            row +=1
            under_col = 0
        bt = ct.CTkButton(self, text = "valider", command = lambda : self.contentGet())
        bt.grid(row = row, column = 0, padx = 10, pady = 10)


    def contentGet(self):
        self.edges = {}
        for i in range(len(self.cb_list)):
            liste = []
            for y in range(len(self.cb_list[i])):
                if self.cb_list[i][y].get():
                    liste.append(self.nodes[y])
            self.edges[self.nodes[i]] = liste
        self.destroy()


    def return_value(self):
        self.wait_window()
        return self.edges




class NodesTopLevelWin(ct.CTkToplevel):

    def __init__(self, nodes = None):
        super().__init__()

        self.grab_set()

        self.values = [] if nodes == None else nodes
        self.return_values = []
        self.entries = []

        self.max_row = 1

        self.add_bt = ct.CTkButton(self, text = "Ajouter", font= ct.CTkFont(family = "arial", size=15), width= 200, command = lambda : self.addValue())
        self.add_bt.grid(column =0, row = 0, padx = 5, pady = 10, columnspan =2)

        self.validate_bt = ct.CTkButton(self, text = "valider", font= ct.CTkFont(family = "arial", size=15), width= 65, command = lambda : self.contentValidation())
        self.cancel_bt = ct.CTkButton(self, text = "annuler", font= ct.CTkFont(family = "arial", size=15), width= 65, command = lambda : self.on_quit())

        if len(self.values) > 0 :
            for i in range(len(self.values)):
                entry = ct.CTkEntry(self, height= 30, width=200, font= ct.CTkFont(family = "arial", size=15))
                entry.insert(0, self.values[i])
                cross_bt = ct.CTkButton(self, text = "X", font= ct.CTkFont(family = "arial", size=15), text_color="#FC2626", width= 20)
                cross_bt.configure(command= lambda x= cross_bt : self.delValue(x))

                self.entries.append((entry, cross_bt))
                entry.grid(column =0, row = i +1, padx = 5, pady = 5, columnspan =2)
                cross_bt.grid(column = 2, row = i + 1, padx = 5, pady = 5, sticky = "w")

        self.validate_bt.grid(row = self.max_row, column =0, padx = 5, pady = 5)
        self.cancel_bt.grid(row = self.max_row, column =1, padx = 5, pady = 5)


        self.bind("<Escape>", self.on_quit)


    def addValue(self):
        entry = ct.CTkEntry(self, height= 30, width=200, font= ct.CTkFont(family = "arial", size=15))
        cross_bt = ct.CTkButton(self, text = "X", font= ct.CTkFont(family = "arial", size=15), text_color="#FC2626", width= 20)
        cross_bt.configure(command= lambda x= cross_bt : self.delValue(x))
        
        self.entries.append((entry, cross_bt))
        
        entry.grid(column =0, row = self.max_row, padx = 5, pady = 5, columnspan =2)
        cross_bt.grid(column = 2, row = self.max_row, padx = 5, pady = 5, sticky = "w")
        self.max_row += 1
        self.validate_bt.grid_configure(row = self.max_row)
        self.cancel_bt.grid_configure(row = self.max_row)

    
    def delValue(self, cross):
        for entries in self.entries :
            if entries[1] == cross :
                entries[0].destroy()
                entries[1].destroy()
                del self.entries[self.entries.index(entries)]


    def on_quit(self, event):
        self.destroy()

 
    def contentValidation(self):
        print(self.entries)
        for entry in self.entries :
            val =entry[0].get()
            if val != "" :
                self.return_values.append(val)
        self.destroy()


    def contentGet(self):
        self.wait_window()
        return self.return_values


inter = interface()
inter.mainloop()
