import tkinter as tk
import tempfile
import webbrowser
from tkinter import filedialog, simpledialog, messagebox
from bs4 import BeautifulSoup

class EditorHTML:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto Editor HTML (Grupo 8)")
        self.current_file = None

        self.text_area = tk.Text(self.root, wrap="word", undo=True)
        self.text_area.pack(expand=True, fill="both", side="left")
        
        self.text_area.bind("<Return>", self.insertar_tab)
        self.text_area.bind("<KeyRelease>", self.on_key_release)

        self.scroll = tk.Scrollbar(self.root, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side="right", fill="y")

        self.num_lineas = tk.Text(self.root, width=4, padx=3, takefocus=0, border=0, background='lightgrey', state='disabled')
        self.num_lineas.pack(side="left", fill="y")

        self.numeroDeLineas()

        # Lista de palabras reservadas de HTML
        self.palabras_reservadas = [
            "html", "/html", "head", "/head", "title", "/title", "base", "/base", "link", "/link", "meta", "/meta", "style", "/style", "script", "/script", "noscript", "/noscript",
            "body", "/body", "section", "/section", "nav", "/nav", "article", "/article", "aside", "/aside", "h1", "/h1", "h2", "/h2", "h3", "/h3", "h4", "/h4", "h5", "/h5", "h6", "/h6",
            "header", "/header", "footer", "/footer", "address", "/address", "main", "/main", "p", "/p", "hr", "pre", "/pre", "blockquote", "/blockquote", "ol", "/ol", "ul", "/ul",
            "li", "/li", "dl", "/dl", "dt", "/dt", "dd", "/dd", "figure", "/figure", "figcaption", "/figcaption", "div", "/div", "a", "/a", "em", "/em", "strong", "/strong", "small", "/small",
            "s", "/s", "cite", "/cite", "q", "/q", "dfn", "/dfn", "abbr", "/abbr", "data", "/data", "time", "/time", "code", "/code", "var", "/var", "samp", "/samp", "kbd", "/kbd",
            "sub", "/sub", "sup", "/sup", "i", "/i", "b", "/b", "u", "/u", "mark", "/mark", "ruby", "/ruby", "rt", "/rt", "rp", "/rp", "bdi", "/bdi", "bdo", "/bdo", "span", "/span",
            "br", "wbr", "ins", "/ins", "del", "/del", "picture", "/picture", "source", "/source", "img", "iframe", "/iframe", "embed", "/embed", "object", "/object",
            "param", "video", "/video", "audio", "/audio", "track", "/track", "map", "/map", "area", "/area", "table", "/table", "caption", "/caption", "colgroup", "/colgroup",
            "col", "/col", "tbody", "/tbody", "thead", "/thead", "tfoot", "/tfoot", "tr", "/tr", "td", "/td", "th", "/th", "form", "/form", "label", "/label", "input", "button", "/button",
            "select", "/select", "datalist", "/datalist", "optgroup", "/optgroup", "option", "/option", "textarea", "/textarea", "output", "/output", "progress", "/progress", "meter", "/meter",
            "fieldset", "/fieldset", "legend", "/legend", "details", "/details", "summary", "/summary", "dialog", "/dialog", "template", "/template", "canvas", "/canvas", "!DOCTYPE html"
        ]

        # Botón Indentar
        self.indentar_button = tk.Button(self.root, text="Indentar", command=self.indentar_texto_con_dom)
        self.indentar_button.pack()

        # Botón Graficar DOM
        self.dom_button = tk.Button(self.root, text="Graficar DOM", command=self.graficar_dom)
        self.dom_button.pack()

        # Menú
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self.nuevo_archivo)
        file_menu.add_command(label="Abrir", command=self.abrir_archivo)
        file_menu.add_command(label="Guardar", command=self.guardar_archivo)
        file_menu.add_command(label="Guardar como...", command=self.guardar_como)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.salir)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        # Menú Edición
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Ir a...", command=self.ir_a_linea)
        edit_menu.add_command(label="Buscar", command=self.buscar)
        edit_menu.add_command(label="Reemplazar", command=self.reemplazar)
        menubar.add_cascade(label="Edición", menu=edit_menu)

        # Menú Impresión
        print_menu = tk.Menu(menubar, tearoff=0)
        print_menu.add_command(label="Imprimir", command=self.imprimir)
        menubar.add_cascade(label="Imprimir", menu=print_menu)

        self.root.config(menu=menubar)

        # Canvas para mostrar el gráfico DOM
        self.dom_canvas = tk.Canvas(self.root, width=400, height=600, bg='white')
        self.dom_canvas.pack(side="right", fill="both", expand=True)

    def on_key_release(self, event=None):
        self.numeroDeLineas()
        self.resaltar_palabras_reservadas()
        self.graficar_dom_en_tiempo_real()

    def numeroDeLineas(self, event=None):
        self.num_lineas.config(state='normal')
        self.num_lineas.delete('1.0', 'end')
        for i in range(1, int(self.text_area.index('end').split('.')[0])):
            self.num_lineas.insert('end', f'{i}\n')
        self.num_lineas.config(state='disabled')

    def resaltar_palabras_reservadas(self, event=None):
        self.text_area.tag_remove('reservada', '1.0', tk.END)
        texto = self.text_area.get('1.0', tk.END)
        for palabra in self.palabras_reservadas:
            start = '1.0'
            palabra_completa = f'<{palabra}>'
            palabra_completa2 = f'<{palabra} '  # para etiquetas con atributos
            while True:
                pos = self.text_area.search(palabra_completa, start, stopindex=tk.END)
                pos2 = self.text_area.search(palabra_completa2, start, stopindex=tk.END)
                if not pos and not pos2:
                    break
                if pos and (not pos2 or pos < pos2):
                    end = f"{pos}+{len(palabra_completa)}c"
                    start = end
                    self.text_area.tag_add('reservada', pos, end)
                elif pos2:
                    end = f"{pos2}+{len(palabra_completa2)}c"
                    start = end
                    self.text_area.tag_add('reservada', pos2, end)
                else:
                    break

        self.text_area.tag_config('reservada', foreground='blue')

    def insertar_tab(self, event):
        linea_actual = self.text_area.index(tk.INSERT).split(".")[0]
        contenido_linea = self.text_area.get(f"{linea_actual}.0", f"{linea_actual}.end").strip()
        tabs = ""
        for char in contenido_linea:
            if char == "<":
                tabs += "    "
            elif char == ">":
                break
        self.text_area.insert(tk.INSERT, "\n" + tabs)
        return 'break'

    def indentar_texto_con_dom(self):
        texto = self.text_area.get(1.0, tk.END)
        try:
            soup = BeautifulSoup(texto, 'html.parser')
            indented_text = soup.prettify()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, indented_text)
        except Exception as e:
            print("Error al indentar el texto:", e)

    def nuevo_archivo(self):
        self.text_area.delete(1.0, tk.END)
        self.numeroDeLineas()
        self.resaltar_palabras_reservadas()

    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos HTML", "*.html"), ("Todos los archivos", "*.*")])
        if archivo:
            self.current_file = archivo
            with open(archivo, "r") as f:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, f.read())
                self.numeroDeLineas()
                self.resaltar_palabras_reservadas()

    def guardar_archivo(self):
        if self.current_file:
            with open(self.current_file, "w") as f:
                texto = self.text_area.get(1.0, tk.END)
                f.write(texto)
        else:
            self.guardar_como() #Si no hay archivo actual, se ejecuta la funcion de Guardar como.

    def guardar_como(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("Archivos HTML", "*.html"), ("Todos los archivos", "*.*")])
        if archivo:
            with open(archivo, "w") as f:
                texto = self.text_area.get(1.0, tk.END)
                f.write(texto)

    def salir(self):
        self.root.quit()

    def buscar(self):
        self.text_area.tag_remove("resaltado", "1.0", tk.END)
        buscar = simpledialog.askstring("Buscar", "Buscar:")
        if buscar:
            start = "1.0"
            ocurrencias_encontradas = False
            while True:
                start = self.text_area.search(buscar, start, stopindex=tk.END)
                if not start:
                    break
                ocurrencias_encontradas = True
                end = f"{start}+{len(buscar)}c"
                self.text_area.tag_add("resaltado", start, end)  # Agregar resaltado
                self.text_area.tag_config("resaltado", background="yellow")  # Configurar color de fondo
                self.text_area.mark_set("insert", start)
                self.text_area.see(start)
                self.text_area.focus_set()
                start = end

            if not ocurrencias_encontradas:
                messagebox.showinfo("Palabra no encontrada", f"No se encontró la palabra '{buscar}' en el documento actual.")

    def reemplazar(self):
        buscar = simpledialog.askstring("Buscar", "Buscar:")
        if buscar:
            reemplazar = simpledialog.askstring("Reemplazar", "Reemplazar por:")
            if reemplazar:
                start = "1.0"
                ocurrencias_reemplazadas = 0
                while True:
                    start = self.text_area.search(buscar, start, stopindex=tk.END)
                    if not start:
                        break
                    ocurrencias_reemplazadas += 1
                    end = f"{start}+{len(buscar)}c"
                    self.text_area.delete(start, end)
                    self.text_area.insert(start, reemplazar)
                    self.text_area.mark_set("insert", start)
                    self.text_area.see(start)
                    self.text_area.focus_set()
                    start = end

                if ocurrencias_reemplazadas == 0:
                    messagebox.showinfo("Palabra no encontrada", f"No se encontró la palabra '{buscar}' en el documento actual.")

    def ir_a_linea(self):
        numero_linea = simpledialog.askinteger("Ir a linea", "Numero de linea: ")
        if numero_linea:
            linea = f"{numero_linea}.0"
            end = f"{numero_linea + 1}.0"
            self.text_area.tag_remove("resaltado", "1.0", tk.END)
            self.text_area.tag_add("resaltado", linea, end)
            self.text_area.tag_config("resaltado", background="yellow")
            self.text_area.mark_set("insert", linea)
            self.text_area.see(linea)
            self.text_area.focus_set()
            if not self.text_area.tag_ranges("resaltado"):
                messagebox.showinfo("Linea no encontrada", f"No se encontro la linea {numero_linea}.")

    def imprimir(self):
        #Guardar el contenido actual en un archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as tmp_file:
            tmp_file.write(self.text_area.get(1.0, tk.END))

        #Abrir el archivo temporal en el navegador web para imprimir
        webbrowser.open(tmp_file.name, new=2)

    def graficar_dom(self):
        texto_html = self.text_area.get(1.0, tk.END)
        try:
            soup = BeautifulSoup(texto_html, 'html.parser')
            self.dibujar_nodos(self.dom_canvas, soup, 200, 50)
        except Exception as e:
            messagebox.showerror("Error", f"Error al graficar el DOM: {e}")

    def dibujar_nodos(self, canvas, nodo, x, y, parent_coords=None):
        if nodo.name:
            # Dibujar el nodo
            canvas.create_oval(x - 20, y - 10, x + 20, y + 10, fill="lightblue")
            canvas.create_text(x, y, text=nodo.name, font=("Helvetica", 10, "bold"))
            
            if parent_coords:
                canvas.create_line(parent_coords[0], parent_coords[1], x, y)
            
            # Dibujar los hijos recursivamente
            if nodo.contents:
                nivel_y = y + 50
                cantidad_hijos = len([child for child in nodo.contents if child.name])
                inicio_x = x - (cantidad_hijos - 1) * 50
                for hijo in nodo.contents:
                    if hijo.name:
                        self.dibujar_nodos(canvas, hijo, inicio_x, nivel_y, (x, y))
                        inicio_x += 100
        elif nodo.string and nodo.string.strip():
            # Dibujar el nodo de texto
            canvas.create_text(x, y, text=nodo.string.strip(), font=("Helvetica", 10))

    def graficar_dom_en_tiempo_real(self):
        # Borrar el contenido previo del canvas
        self.dom_canvas.delete("all")
        
        texto_html = self.text_area.get(1.0, tk.END)
        try:
            soup = BeautifulSoup(texto_html, 'html.parser')
            self.dibujar_nodos(self.dom_canvas, soup, 200, 50)
        except Exception as e:
            print("Error al graficar el DOM en tiempo real:", e)

def main():
    root = tk.Tk()
    editor = EditorHTML(root)
    root.mainloop()

if __name__ == "__main__":
    main()
