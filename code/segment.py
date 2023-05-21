import cv2
import os
import numpy as np
from PIL import Image
import skimage


def smoothFilter(img):
    kernel = np.ones((5, 5), np.float32) / 25
    return cv2.filter2D(img, -1, kernel)


def gaussFilter(img):
    return cv2.GaussianBlur(img, (5, 5), 0)


def OtsuMethod(img, thr):
    ret, th = cv2.threshold(img, thr, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return ret, th


def calcArea(x1, y1, x2, y2, x3, y3, x4, y4):
    # Calcular las diagonales
    diagonal_mayor = ((x4 - x2) ** 2 + (y4 - y2) ** 2) ** 0.5
    diagonal_menor = ((x3 - x1) ** 2 + (y3 - y1) ** 2) ** 0.5

    # Calcular el área del rombo
    area = (diagonal_mayor * diagonal_menor) / 2

    return area


def loadImages(src, dst):
    # Guardamos las direcciones de las carpetas donde estaran las imagenes y donde guardaremos las imagenes
    input_images_path = src
    files_names = os.listdir(input_images_path)

    output_images_path = dst

    if not os.path.exists(output_images_path):
        os.makedirs(output_images_path)
        print("Directorio creado: ", output_images_path)

    count = 0
    for file_name in files_names:

        image_path = input_images_path + "/" + file_name
        image = cv2.imread(image_path)
        if image is None:
            continue

        cv2.imwrite(output_images_path +
                    str(count) + ".jpg", image)
        count += 1


def segmentImage(src1, src2):
    # Guardamos las imagenes
    img1 = cv2.imread(src1)
    img1 = gaussFilter(img1)

    img2 = cv2.imread(src2)
    img2 = gaussFilter(img2)

    res = cv2.absdiff(img2, img1)
    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    _, res = cv2.threshold(res, 50, 255, cv2.THRESH_BINARY)
    #cv2.imshow('Imagen segmentada', res)

    # Aplicamos erosion
    kernel = np.ones((3, 3), np.uint8)
    img_ero = cv2.erode(res, kernel, iterations=1)
    #cv2.imshow('Imagen erosionada', erosionado)

    # Aplicamos dilate
    kernel = np.ones((10, 10), np.uint8)
    img_dil = cv2.dilate(img_ero, kernel, iterations=1)
    #cv2.imshow('Imagen segmentada', img_dil)

    cv2.waitKey(0)

    return img_dil


def segmentImagePerspective(src1, src2, H, file):
    # Guardamos las imagenes
    img1 = cv2.imread(src1)
    img1 = gaussFilter(img1)

    img2 = cv2.imread(src2)
    img2 = gaussFilter(img2)

    # Dimensiones de la imagen resultante
    wp_x = 1080
    wp_y = 1080

    if (H.all() == None):
        # Calculamos la perspectiva
        image_points = []  # Para guardar los puntos seleccionados

        # Funcion para leer inputs del raton
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                # Añadir el punto a la lista
                image_points.append((x, y))
                # Marcamos con un circulo el punto seleccionado
                cv2.circle(img1, (x, y), 5, (0, 255, 0), -1)
                #cv2.imshow('Image', img1)

        # Creamos una ventana junto la funcion creada anteriormente
        cv2.namedWindow('Image')
        cv2.setMouseCallback('Image', mouse_callback)
        #cv2.imshow('Image', img1)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Convertimos los puntos a un array numpy
        image_points = np.array(image_points, dtype=np.float32)

        print('Selected Image Points:')
        print(image_points)

        # Definimos los puntos de la imagen output
        #world_points = np.array([[0, 0], [image.shape[1], 0], [image.shape[1], image.shape[0]], [0, image.shape[0]]], dtype=np.float32)
        world_points = np.array(
            [[0, 0], [wp_x, 0], [wp_x, wp_y], [0, wp_y]], dtype=np.float32)

        # Calculamos la matriz de homografia
        H = cv2.getPerspectiveTransform(image_points, world_points)
        # Guardamos la matriz
        np.save(file, H)

    # Aplicamos la matriz
    img1_output = cv2.warpPerspective(img1, H, (wp_x, wp_y))
    img2_output = cv2.warpPerspective(img2, H, (wp_x, wp_y))
    #cv2.imshow('Imagen 2', img2_output)

    # Calculamos la segmentación
    res = cv2.absdiff(img2_output, img1_output)
    res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    _, res = cv2.threshold(res, 50, 255, cv2.THRESH_BINARY)
    #cv2.imshow('Imagen segmentada', res)

    # Aplicamos erosion
    kernel = np.ones((3, 3), np.uint8)
    img_ero = cv2.erode(res, kernel, iterations=1)
    #cv2.imshow('Imagen erosionada', erosionado)

    # Aplicamos dilate
    kernel = np.ones((10, 10), np.uint8)
    img_dil = cv2.dilate(img_ero, kernel, iterations=1)
    #cv2.imshow('Imagen segmentada', img_dil)

    cv2.waitKey(0)

    return img_dil, img2_output


def calculateLots(coords, img, src1, src2):
    plaza_libre = 0
    img_coches = cv2.imread(src1)
    img_plazas = cv2.imread(src2)
    vehicle = []
    print()
    for coor in coords:
        print("\nCoords nuevas")

        # Crear una máscara para la región de interés
        mascara = np.zeros(img.shape[:2], dtype=np.uint8)
        puntos = np.array([(coor[0][0], coor[0][1]), (coor[1][0], coor[1][1]),
                           (coor[2][0], coor[2][1]), (coor[3][0], coor[3][1])], np.int32)
        cv2.fillPoly(mascara, [puntos], (255, 255, 255))

        # Obtener los valores de la región de interés
        valores_region = cv2.bitwise_and(img, img, mask=mascara)

        pixel_one = np.count_nonzero(valores_region == 255)
        area = int(calcArea(coor[0][0], coor[0][1], coor[1][0], coor[1]
                            [1], coor[2][0], coor[2][1], coor[3][0], coor[3][1]))

        print(str(pixel_one) + ' / ' + str(area))
        coor_array = np.asarray(coor, dtype=np.int32)
        coor_array = coor_array.reshape((-1, 1, 2))
        if (pixel_one > area * 0.5):
            print("Hay vehiculo")
            img_coches = cv2.polylines(
                img_coches, [coor_array], True, (0, 0, 255))
            img_plazas = cv2.fillPoly(img_plazas, [coor_array], (0, 0, 255))
            vehicle.append(1)
        else:
            print("No hay vehiculo")
            plaza_libre += 1
            img_plazas = cv2.fillPoly(img_plazas, [coor_array], (0, 255, 0))
            vehicle.append(0)

    print("\nHay", str(plaza_libre), "plazas libres")
    #cv2.imshow("img_coches", img_coches)
    #cv2.imshow("img_plazas", img_plazas)
    #cv2.waitKey(0)

    return vehicle


def makeMean(src, dst):
    # Calcular imagen mean
    # Access all PNG files in directory
    allfiles = os.listdir(src)  # src
    imlist = [filename for filename in allfiles if filename[-4:]
              in [".jpg", ".JPG"]]

    # Assuming all images are the same size, get dimensions of first image
    w, h = Image.open(src + str(imlist[0])).size
    N = len(imlist)

    # Create a numpy array of floats to store the average (assume RGB images)
    arr = np.zeros((h, w, N))

    # Build up average pixel intensities, casting each image as an array of floats
    i = 0
    for im in imlist:
        img = skimage.io.imread(src + im)
        img = skimage.color.rgb2gray(img)
        arr[:, :, i] = img
        i += 1

    mean = np.mean(arr, 2)

    skimage.io.imshow(mean), skimage.io.show(
    ), skimage.io.imsave(dst, mean)