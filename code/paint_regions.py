import matplotlib.pyplot as plt
import cv2
import pickle
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

def lotColor(filename, vehicle):
    patches_full = []
    patches_empty = []
    regions = filename  # Nombre del archivo donde estén las posiciones de las plazas
    with open(regions, "rb") as f:
        parked_car_boxes = pickle.load(f)
        i = 0
        for p in parked_car_boxes:
            if (vehicle[i] == 1):
                # Plazas ocupadas, se guarda el poligono con el color rojo
                patches_full.append(Polygon(p, fill=True, color=[1, 0, 0]))
            else:
                # Plazas vacías, se guarda el poligono con el color verde
                patches_empty.append(Polygon(p, fill=True, color=[0, 1, 0]))
            i += 1

        # Crea el conjunto de poligonos a dibujar, cuanto mayor alfa, más solido será el color
        pF = PatchCollection(patches_full, alpha=0.5, match_original=True)
        pE = PatchCollection(patches_empty, alpha=0.5, match_original=True)

        return pE, pF

def paintRegions(img, path, vehicle):
    # Crear figura y eje sobre los que dibujar
    _, ax = plt.subplots()
    # Imagen sobre la que pintar las plazas
    image = cv2.imread(img)
    # Convertir de BGR a RGB porque cv2 es especialito
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Dibujar imagen sobre el eje
    ax.imshow(image)
    # Llamar a la función que asigna los colores de las plazas y crea los poligonos
    pE, pF = lotColor(path, vehicle)
    # Dibujar los poligonos sobre el eje
    ax.add_collection(pF)
    ax.add_collection(pE)
    # Mostrar la figura
    plt.show()
    
