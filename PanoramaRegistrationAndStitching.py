import cv2
import numpy as np
import matplotlib.pyplot as plt
import random


def findIndexsAndValuesInImg2(pos1, pos2, pos1_4, amount: int):
    if amount == 4:
        p1 = None
        p2 = None
        p3 = None
        p4 = None
        ip1 = None
        ip2 = None
        ip3 = None
        ip4 = None
        for i in range(pos1.shape[0]):
            if pos1[i][0] == pos1_4[0][0] and pos1[i][1] == pos1_4[0][1]:
                p1 = pos2[i]
                ip1 = i
            elif pos1[i][0] == pos1_4[1][0] and pos1[i][1] == pos1_4[1][1]:
                p2 = pos2[i]
                ip2 = i
            elif pos1[i][0] == pos1_4[2][0] and pos1[i][1] == pos1_4[2][1]:
                p3 = pos2[i]
                ip3 = i
            elif pos1[i][0] == pos1_4[3][0] and pos1[i][1] == pos1_4[3][1]:
                p4 = pos2[i]
                ip4 = i
        real_pos2_val = np.array([p1, p2, p3, p4])
        real_pos2_ind = np.array([ip1, ip2, ip3, ip4])
        return real_pos2_val, real_pos2_ind
    elif amount == 1:
        p1 = None
        ip1 = None
        for i in range(pos1.shape[0]):
            if pos1[i][0] == pos1_4[0][0] and pos1[i][1] == pos1_4[0][1]:
                p1 = pos2[i]
                ip1 = i
        real_pos2_val = p1
        real_pos2_ind = ip1
        return real_pos2_val, real_pos2_ind


# ===================================
# =======OpenCV match features=======
# ===================================
def matchFeatures(img1: np.ndarray, img2: np.ndarray):
    """
    Find match point between images(can include outliers).
    Use Brute Force(BF) matching.
    :param img1
    :param img2
    :return: set of points coordinates in both images
             , pos1 and pos2, of size nx2 that are most likely matched.
    """
    orb = cv2.ORB_create()

    #  Find the key points and their descriptors with the orb detector
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    # The matcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Create matches of the descriptors, then sort them based on their distances
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    list_kp1 = [kp1[mat.queryIdx].pt for mat in matches]
    list_kp2 = [kp2[mat.trainIdx].pt for mat in matches]
    pos1 = np.array(list_kp1)
    pos2 = np.array(list_kp2)

    # Checking if the matching points between the images in the right position
    # for i in range(len(list_kp1)):
    #     y1, x1 = int(list_kp1[i][0]), int(list_kp1[i][1])  # x is number of row, y is number of column
    #     y2, x2 = int(list_kp2[i][0]), int(list_kp2[i][1])
    #     print("intensities match : img1[x1][y1], img2[x2][y2] ", img1[x1][y1], img2[x2][y2])
    #     print("location of pixel in img1 : ", x1, y1)
    #     print("location of pixel in img2 : ", x2, y2)
    #     plt.imshow(img1)
    #     plt.show()
    #     plt.imshow(img2)
    #     plt.show()

    # Display 50 matches
    img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches[:50], None, flags=2)
    plt.imshow(img3)
    plt.show()

    return pos1, pos2


def ApplyHomography(pos1: np.ndarray, H12: np.ndarray) -> np.ndarray:
    pos2 = np.zeros(pos1.shape)
    i = 0
    j = 0
    for point in pos1:
        homog_point = np.array([point[0], point[1], 1])
        nhomog_point = np.dot(H12, homog_point.T)
        x = nhomog_point[0]/nhomog_point[2]
        y = nhomog_point[1]/nhomog_point[2]
        res_point = np.array([x, y])
        pos2[i] = res_point
        i += 1
    return pos2


def leastSquareHomograpy(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    x1, y1 = p1[0][0], p1[0][1]
    x2, y2 = p1[1][0], p1[1][1]
    x3, y3 = p1[2][0], p1[2][1]
    x4, y4 = p1[3][0], p1[3][1]
    xp1, yp1 = p2[0][0], p2[0][1]
    xp2, yp2 = p2[1][0], p2[1][1]
    xp3, yp3 = p2[2][0], p2[2][1]
    xp4, yp4 = p2[3][0], p2[3][1]

    A = [
        [-x1, -y1, -1, 0, 0, 0, x1 * xp1, y1 * xp1, xp1],
        [0, 0, 0, -x1, -y1, -1, x1 * yp1, y1 * yp1, yp1],
        [-x2, -y2, -1, 0, 0, 0, x2 * xp2, y2 * xp2, xp2],
        [0, 0, 0, -x2, -y2, -1, x2 * yp2, y2 * yp2, yp2],
        [-x3, -y3, -1, 0, 0, 0, x3 * xp3, y3 * xp3, xp3],
        [0, 0, 0, -x3, -y3, -1, x3 * yp3, y3 * yp3, yp3],
        [-x4, -y4, -1, 0, 0, 0, x4 * xp4, y4 * xp4, xp4],
        [0, 0, 0, -x4, -y4, -1, x4 * yp4, y4 * yp4, yp4]]

    U, S, V = np.linalg.svd(A)
    m = min(S)
    # print("min = ", m)
    # print("S = ", S)
    # print("V' = ", np.dot(V, V.T))

    H = V[:, V.shape[1] - 1]
    H = np.reshape(H, (3, 3))
    # print("H = ", H)

    # Test the result matrix
    t_H, mask = cv2.findHomography(p1, p2, method=0)
    print("t_H (homography matrix)= ", t_H)
    return t_H


def E(H12: np.ndarray, pos1_1: np.ndarray, pos1: np.ndarray, pos2: np.ndarray, inlierTol: int) -> (int, int):
    """
    The method find the inliers and outliers of matching points for given set of
    4 points.
    The method use Squared Euclidean Distance to find inliers points :
    E_i = || P' - P ||^2 < inlierTol
    when P' - is the transformed set of 4 points
    and P - is the 4 matching point in image 2
    :param H12: Homography matrix
    :param pos1_1: Set of 1 point in image 1
    :param pos1: Full set of points in image 1
    :param pos2: Full set of points in image 2
    :param inlierTol: Constant value to inlier point approximation
    :return:
    """
    pred_pos2 = ApplyHomography(pos1_1, H12)

    # find the corresponding point in image 2
    real_pos2_val, real_pos2_ind = findIndexsAndValuesInImg2(pos1, pos2, pos1_1, 1)
    print("pred_pos2 = ", pred_pos2)
    print("real_pos2 = ", real_pos2_val)

    # Find E = || P' - P ||^2
    sed = (np.linalg.norm(pred_pos2-real_pos2_val))**2
    print("sed = ", sed)

    # Determine if E < inlierTol
    if sed < inlierTol:
        return 1, real_pos2_ind
    else:
        return 0


def ransacHomography(pos1: np.ndarray, pos2: np.ndarray, numIter: int, inlierTol: int) -> (np.ndarray, np.ndarray):
    maxIliners = []
    for i in range(numIter):
        r_p1 = random.choice(pos1)
        r_p2 = random.choice(pos1)
        r_p3 = random.choice(pos1)
        r_p4 = random.choice(pos1)
        print("r_p1 = ", r_p1)
        print("r_p2 = ", r_p2)
        print("r_p3 = ", r_p3)
        print("r_p4 = ", r_p4)
        rp_4 = np.array([r_p1, r_p2, r_p3, r_p4])
        real_pos2_val, real_pos2_ind = findIndexsAndValuesInImg2(pos1, pos2, rp_4, 4)
        H = leastSquareHomograpy(rp_4, real_pos2_val)

        # Compute E to full pos1 set and bind the inliers
        inliers = []
        for j in pos1:
            dis, match = E(H, np.array([j]), pos1, pos2, inlierTol)
            if dis == 1:
                inliers.append(match)

        # Find the maximum inliers set
        print("len(inliers) = ", len(inliers))
        if len(inliers) > len(maxIliners):
            maxIliners = inliers
            print("maxIliners = ", maxIliners)

    # Calculate the finally homography matrix by inliers
    # /////////////////your code//////////////////

    # return the finally homography matrix and the set of maxInliers
    return maxIliners


# ===================================
# ===============Main================
# ===================================
img1 = cv2.imread('backyard1.jpg')
img2 = cv2.imread('backyard2.jpg')
img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
pos1, pos2 = matchFeatures(img1, img2)
# t_p1 = np.array([pos1[0], pos1[1], pos1[2], pos1[3]])
# t_p2 = np.array([pos2[0], pos2[1], pos2[2], pos2[3]])
# H = leastSquareHomograpy(t_p1, t_p2)
# count = E(H, t_p1, pos1, pos2, 1)
# print(count)
ransacHomography(pos1, pos2, 20, 1)
# print(t_pos2)