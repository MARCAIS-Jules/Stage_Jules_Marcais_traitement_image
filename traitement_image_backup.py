# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 15:19:42 2021

@author: Asus
"""


import os
from skimage import io, measure, filters, morphology, segmentation, feature, color
import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use('TkAgg')
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy import ndimage as ndi
import tkinter as tk
from PIL import Image, ImageTk


    
def calc_histogrammes(image):
    '''
    Entrée : image au format np array (N,M,3)
    Sortie : 3 histogrammes (RGB) au format tuple contenant 2 arrays
    '''
    array_r = image[:,:,0]
    array_g = image[:,:,1]
    array_b = image[:,:,2]
    
    histo_r = np.histogram(array_r, bins = range(257))
    histo_g = np.histogram(array_g, bins = range(257))
    histo_b = np.histogram(array_b, bins = range(257))

    return histo_r, histo_g, histo_b

def calc_mask(image,n):
    '''
    Entrée : image au format np array (N,M,3)
    
    Sortie : mask (objet au premier plan) au format liste de listes de booleens
    '''

    array_r = image[:,:,0]
    #array_v = image[:,:,1]
    #array_b = image[:,:,2]
    #array_moyen = (array_r + array_v )/2
    '''
    val = filters.threshold_otsu(array_r)
    mask = array_r > val
    '''
    thresholds = filters.threshold_multiotsu(array_r, classes = n)
    regions = np.digitize(array_r, bins=thresholds)
    regions_max = regions.copy()
    regions_max = regions_max == n-1 #on prend le seuil le plus élevé = la partie la plus claire de l'image
    print(regions_max)
    #regions_colorized = color.label2rgb(regions)
    
    
    return regions_max

def calc_contours(mask):
    '''
    Entrée : mask (objet au premier plan) au format liste de listes de 0 et de 1
    Sortie: contours des objets au format liste d'arrays
    '''
    
    contours = measure.find_contours(mask, 0.9)

    return contours

def max_array(l_array):
    '''
    Entrée : liste d'arrays
    Sortie : array le plus grand de la liste
    '''
    
    taille = 0
    for elem in l_array:
        if len(elem) > taille:
            taille = len(elem)
            array_max = elem
    
    return array_max

def filtre_array(l_array, array_max, seuil):
    '''
    Entrée : liste d'arrays
    Sortie : liste d'arrays dont on a enlevé les plus petits
    '''
    
    len_min = seuil*len(array_max)
    array_filtre = []
    for elem in l_array:
        if len(elem) > len_min:
            array_filtre.append(elem)
            
    return array_filtre

def erosion(mask, k):
    '''
    Entrée : mask : (liste de listes de 0 et de 1)
             k : entier correspondant au nombre d'érosions successives
    Sortie : même format que mask mais avec erosion et dilatation
    '''
    
    mask_2 = morphology.binary_erosion(mask, morphology.diamond(k)).astype(np.bool)
    mask_2 = morphology.binary_dilation(mask_2, morphology.diamond(k-1)).astype(np.bool)
    
    return mask_2

def affichage(image, mask, histo_r, histo_g, histo_b, contours,contour_bool):
    '''
    Entrée : image (N,M,3)
             3 histogrammes : tuple contenant 2 arrays
             contours : liste d'arrays
    Sortie : Affiche l'image avec les contours à droite des 3 histos superposés 
    '''
    fig, axs = plt.subplots(1,2)
    
    #affichage des histogrammes
    '''
    axs.plot(histo_r[1][:-1],histo_r[0], color = 'r')
    axs.plot(histo_g[1][:-1],histo_g[0], color = 'g')
    axs.plot(histo_b[1][:-1],histo_b[0], color = 'b')
    '''
    #affiche image IR
    axs[0].imshow(image)
    axs[0].axis('image')
    
    #affichage masque + contours
    axs[1].imshow(mask)
    axs[1].axis('image')
    
    if contour_bool:
        for contour in contours:
            axs[1].plot(contour[:, 1], contour[:, 0], linewidth=2)
            axs[1].plot(contour[:, 1], contour[:, 0], linewidth=2)
        #print(contours)
    
    '''
    axs[0].set_xticks([])
    axs[0].set_yticks([])    
    axs[1].set_xticks([])
    axs[1].set_yticks([])    
    '''
    plt.show()

def histo_objets(image, coordonnees):
    '''
    Entrée : image (N,M,3)
             coordonnées au format liste d'arrays
    Sortie :
    '''
    array_r = image[:,:,0]
    array_g = image[:,:,1]
    array_b = image[:,:,2]
    
    n = len(coordonnees)
    fig_hist,ax_hist = plt.subplots(3,n)
    
    l_pixel_r = []
    l_pixel_g = []
    l_pixel_b = []
    for k in range(n):
        for point in coordonnees[k]:
            l_pixel_r.append(array_r[point[0],point[1]])
            l_pixel_g.append(array_g[point[0],point[1]])
            l_pixel_b.append(array_b[point[0],point[1]])
        histo_r = np.histogram(l_pixel_r, bins = range(257))
        histo_g = np.histogram(l_pixel_g, bins = range(257))
        histo_b = np.histogram(l_pixel_b, bins = range(257))
        
        try:
            ax_hist[0][k].plot(histo_r[1][:-1],histo_r[0], color = 'r')
            ax_hist[1][k].plot(histo_g[1][:-1],histo_g[0], color = 'g')
            ax_hist[2][k].plot(histo_b[1][:-1],histo_b[0], color = 'b')
        except TypeError:
            ax_hist[0].plot(histo_r[1][:-1],histo_r[0], color = 'r')
            ax_hist[1].plot(histo_g[1][:-1],histo_g[0], color = 'g')
            ax_hist[2].plot(histo_b[1][:-1],histo_b[0], color = 'b')
            
    plt.show()

def test_otsu(image,n):
    array_r = image[:,:,1]
        
    # Applying multi-Otsu threshold for the default value, generating
    # three classes.
    thresholds = filters.threshold_multiotsu(array_r,classes = n)
    
    # Using the threshold values, we generate the three regions.
    regions = np.digitize(array_r, bins=thresholds)
    regions_max = regions.copy()
    regions_max = regions_max == n-1 #on prend le seuil le plus élevé = la partie la plus claire de l'image
    print(regions_max)
    
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(10, 3.5))
    
    # Plotting the original image.
    ax[0].imshow(image, cmap='gray')
    ax[0].set_title('Original')
    ax[0].axis('off')
    
    # Plotting the histogram and the two thresholds obtained from
    # multi-Otsu.
    ax[1].hist(array_r.ravel(), bins=255)
    ax[1].set_title('Histogram')
    for thresh in thresholds:
        ax[1].axvline(thresh, color='r')
    
    # Plotting the Multi Otsu result.
    ax[2].imshow(regions, cmap='jet')
    ax[2].set_title('Multi-Otsu result')
    ax[2].axis('off')
    
    plt.subplots_adjust()
    
    plt.show()


''' 
class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.left = tk.Frame(self)
        self.left.pack(side="left")
        
        self.right = tk.Frame(self)
        self.right.pack(side="right")
        
        self.top_right = tk.Frame(self)
        self.top_right.pack(in_=self.right, side="top")
        
        self.label_1 = tk.Label(self, text = "Nom de l'image :")
        self.label_1.pack(in_=self.left)
        
        
        self.value_nom = tk.StringVar() 
        self.entree = tk.Entry(self, textvariable=self.value_nom, width=30)
        self.entree.pack(in_=self.left)
        
        self.value_scale_eros = tk.DoubleVar()
        self.scale_eros = tk.Scale(self, variable=self.value_scale_eros, orient='horizontal', from_=1, to=10,
                                   resolution=1, tickinterval=1, length=350, label="Combien d'erosions successives?")
        self.scale_eros.pack(in_=self.left)
        
        self.value_scale_seuil = tk.DoubleVar()
        self.scale_seuil = tk.Scale(self, variable=self.value_scale_seuil, orient='horizontal', from_=0, to=100,
                                    resolution=1, tickinterval=10, length=350,
                                    label="Seuil en % ?")
        self.scale_seuil.pack(in_=self.left)
        
        self.value_scale_otsu = tk.DoubleVar()
        self.scale_otsu = tk.Scale(self, variable=self.value_scale_otsu, orient='horizontal', from_=2, to=5, 
                                   resolution=1, tickinterval=1, length=350,
                                   label="Combien de seuils dans le multiotsu?")
        self.scale_otsu.pack(in_=self.left)    
        
        
        #self.bouton=tk.Button(self, text="Valider", command=valider)
        self.bouton.pack(in_=self.left)
        self.nrow, self.ncol = image.shape[0:2]
        
        self.image =  ImageTk.PhotoImage(image=Image.fromarray(image))
        self.mask =  ImageTk.PhotoImage(image=Image.fromarray(image))
        
        #affichage images
        self.label_2 = tk.Label(self, width=75, text="Image :")
        self.label_2.pack(in_=self.top_right, side="left")
        self.label_3 = tk.Label(self, width=50, text="Image mask:")
        self.label_3.pack(in_=self.top_right, side="right")
        
        
        self.canvas_1 = tk.Canvas(self, width=100+self.ncol, height=self.nrow)
        self.canvas_1.pack(in_=self.right,side ="left")
        self.image_1 = self.canvas_1.create_image(100,0, anchor="nw", image=self.image)


        #self.canvas_2 = tk.Canvas(self, width=100+self.ncol, height=self.nrow)
        #self.canvas_2.pack(in_=self.right,side="left")
        #self.image_2 = self.canvas_2.create_image(100,0, anchor="nw", image=self.mask)
        '''
'''  
    def plot(self,image,mask):
        fig = Figure(figsize=(6,6))
        gs = fig.add_gridspec(1,2)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        
        #ax1.plot(image)
        ax2.imshow(mask)
        
        #canvas_1 = FigureCanvasTkAgg(ax1, master=self)
        #canvas_1.get_tk_widget().pack()
        canvas_2 = FigureCanvasTkAgg(fig, master=self)
        canvas_2.get_tk_widget().pack()
        '''
'''        
def valider():
    eros = int(fenetre.value_scale_eros.get())
    seuil = fenetre.value_scale_seuil.get()/100
    otsu = int(fenetre.value_scale_otsu.get())
    nom_img = fenetre.value_nom.get()
    
    image = io.imread(path+nom_img)
    fenetre.image =  ImageTk.PhotoImage(image=Image.fromarray(image))
    fenetre.canvas_1.itemconfig(fenetre.image_1,image=fenetre.image)
    
    
    main(nom_img,seuil,eros,otsu,contour_bool) 
 '''       
        
def main(nom_img,seuil,k,n,contour_bool):
    #calcul des histogrammes
    print(seuil,k,n)
    image = io.imread(path + nom_img)
    
    histo_r, histo_g, histo_b = calc_histogrammes(image)
    
    #calcul du masque + erosion
    mask = calc_mask(image,n)
    
    #mask = morphology.binary_dilation(mask, morphology.diamond(5)).astype(np.bool)
    mask = erosion(mask, k)
    mask_label = measure.label(mask)
    #mask_label = erosion(mask_label, k)
    
    '''
    #segmentation = on sépare les objets superposés
    distance = ndi.distance_transform_edt(mask_label)
    coords = feature.peak_local_max(distance, footprint=np.ones((3, 3)), labels=mask_label)
    mask_2 = np.zeros(distance.shape, dtype=bool)
    mask_2[tuple(coords.T)] = True
    markers, _ = ndi.label(mask_2)
    mask_label = segmentation.watershed(-distance, markers, mask=mask_label)
    '''
    properties = measure.regionprops(mask_label)
    
    #on enlève les objets de petites taille
    obj_tailles = [prop.area for prop in properties]
    taille_max = max(obj_tailles)
    for k in range(len(obj_tailles)):
        if obj_tailles[k] < seuil*taille_max: #objet trop petit qui sera enleve
            for ligne in mask_label:
                for i in range(len(ligne)):
                    if ligne[i] == k+1:
                        ligne[i] = 0
    
    mask_label = measure.label(mask_label) #changemebt de couleur pour le contraste
    

    #récupération des propriétés des objets
    properties_act = measure.regionprops(mask_label)
    obj_tailles = [prop.area for prop in properties_act]
    
    taille_moy = sum(obj_tailles)/len(obj_tailles)
    compteur_superpos = 0
    compteur_superpos_2 = 0
    histo_t = np.histogram(obj_tailles)
    #finir histo tailles objet
    for k in range(len(obj_tailles)):
        compteur_superpos += max(int(obj_tailles[k]/taille_moy) - 1,0)
        compteur_superpos_2 += int(obj_tailles[k]/taille_moy)
    print("compteur_superpos =",compteur_superpos)
    print("compteur_superpos_2 =",compteur_superpos_2)
    print("Nombre d'objets :",compteur_superpos + len(obj_tailles))
    
    '''
    #affichage des histogrammes de chaque objet
    coord_act = [prop.coords for prop in properties_act]   
    histo_objets(image, coord_act)
    '''
    
    #calcul des contours
    contours = calc_contours(mask_label)
    
    contour_max = max_array(contours)
    contours_filtre = filtre_array(contours, contour_max, seuil)
    mask_label = measure.label(mask_label) #changemebt de couleur pour le contraste
    #affichage image + contours + histogrammes
    affichage(image, mask_label, histo_r, histo_g, histo_b, contours_filtre,contour_bool)
    
    #fenetre.plot(image,mask_label)


#%% Programme principal
    

#variables
seuil = 3/100
k = 3 #nombre d'érosions sucessives
n = 2 #nombre de classes dans le  threshold multiotsu
contour_bool =  True 
#L, l = 800, 500 #dimensions de la fenetre

#recuperation de l'image
path = os.getcwd() + "\images\\"
nom_img = "tournesols_IR_1.png"
filename = path + nom_img
image = io.imread(filename)

'''
fenetre=GUI()
fenetre.mainloop()
'''
#test_otsu(image,n)

main(nom_img, seuil, k, n,contour_bool)

