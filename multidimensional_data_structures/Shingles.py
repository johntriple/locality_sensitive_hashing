import Bloomfilter as bf
import numpy as np
import random as r
import re
import string

#Η συνάρτηση Parse κάνει προεργασία το αρχείο-είσοδο
def Parse(input_text):
    X = open(input_text, "r+") #Το αρχείο αποθηκεύεται στην μεταβλητή Χ με δικαιώματα read+
    y = X.read() #Διαβάζουμε τα περιεχόμενα του αρχείου
    y = re.sub('[' + string.punctuation + ']', '', y) #Αφαιρούμε τα σημεία στήξης καθώς και το '[',']' και τα αντικαθιστουμε με το κενό.
    y = y.lower() #Μετατρέπουμε κάθε κεφαλαίο χαρακτήρα σε πεζό
    for i in range(len(y)):
        try:
            if (y[i] == '\n' or y[i] == ' ' or y[i] == '\t' or y[i] == '\\'): #έξτρα έλεγχος για να αντικαταστήσουμε και τις αλλαγές γραμμών καθώς και τα tabs με το κενό.
                y = y.replace(y[i], '')
        except IndexError as IE: #Δυναμικό handling της μνήμης καθώς αποδεσμεύουμε τα δεδομένα που "πετάμε"
            break;

    return y

#Η Συνάτρηση Shingles δέχεται το parsed αρχείο και το μέγεθος των shingles και διασπά την πλέον μία λέξη που απαρτίζει ολόκληρο το αρχείο σε shingles μεγέθους k
def Shingles(parsed_text, k):
    shingle = [] #Αρχικοποιήση της λίστας shingles
    for i in range(len(parsed_text) - k + 1):
        shingle.append('')
        for j in range(k):
            shingle[i] += parsed_text[j + i] #Για κάθε k χαρακτήρες στο αρχείο μας κάνε append τη λίστα shingle και τοποθέτησε τη λέξη.

    """Filtering redundant shingles"""
    unique = [] #Αρχικοποιήση της λίστας unique με σκοπό την αφαίρεση των duplicates.

    test = bf.ArrayInit(len(shingle), 0.05) #Εφαρμογή των φίλτρων bloom για την εύρεση duplicate

    N = bf.Hash(len(shingle), len(test)) #Εύρεση του βέλτιστου αριθμού hash functions

    for i in shingle: #Απαλυφή των duplicates με χρήση του φίλτρου.
        not_found = True
        not_found = bf.Check(test, N, i)
        test = bf.Add(test, N, i)
        if not not_found: unique.append(i)

    return unique

"""Η συνάρτηση SMatrix δέχεται ως ορίσματα τα parsed shingles και φτιάχνει ένα Matrix που περιέχει τον αριθμό των φορών που
ένα shingle εμφανίζεται ανά αρχείο."""
def SMatrix(Shingle_type_1, Shingle_type_2):  # dokimh argotera kai gia genikeumeno ari8mo apo shingle inputs
    Merged = Shingle_type_1.copy() #Δημιουργούμε μεταβλητή Merged που θα περιέχει το U των shingles των αρχείων που συγκρίνουμε.
    BloomArr = bf.ArrayInit(len(Shingle_type_1), 0.05) #Χρησιμοποιούμε το bloom filter για να έχουμε ένα πιο αποδοτικό searching για τα στοιχεία.

    k = bf.Hash(len(Shingle_type_1), len(BloomArr)) #Υπολογίζουμε το k των bloom filters.
    for i in Merged:
        BloomArr = bf.Add(BloomArr, k, i) #Προσθέτουμε στο φίλτρο τα στοιχεία του μητρώου.
    for i in Shingle_type_2: #Με την for αυτή αποφεύγουμε το ενδεχόμενο να έχουμε duplicates στην λίστα merged.
        Not_Found = True
        Not_Found = bf.Check(BloomArr, k, i)
        if not Not_Found: Merged.append(i)
    """Akolou8ei kwdikas gia to matrix me ta permutations"""
    Matrix = np.zeros([len(Merged),2]) #Κάνουμε pre-allocation το μητρώο Matrix.

    for i in range(len(Matrix)):
        Matrix[i, 0] = Shingle_type_1.count(Merged[i])
        Matrix[i, 1] = Shingle_type_2.count(Merged[i])

    return Matrix

"""Η συνάρτηση αυτή θα χρησιμοποιηθεί για την κατασκευή των permutations που θα χρησιμοποιηθούν αργότερα."""
def Permutations(Input_Matrix, Number_Of_Permutations):
    lines = len(Input_Matrix[:]) #μέγεθος του matrix όσο είναι τα shingles.
    init = []
    #Κατασκευάζουμε μονοδιάστατη λίστα από το 1 μέχρι τα lines μας και τους δίνουμε τιμές με τη σειρά ξεκινώντας από το 1.
    for i in range(1,lines):
        init.append(i)

    p = []
    #Παίρνουμε την λίστα Init που κατασκευάσαμε πιο πάνω και ανακατεύουμε τα περιεχόμενά της.
    for i in range(Number_Of_Permutations):
        temp = init.copy()
        r.shuffle(temp)
        p.append(temp)
    p = np.transpose(p)
    return p

"""Η συνάρτηση αυτή θα χρησιμοποιηθεί για να δημιουργηθούν τα signature"""
def Signature(Permutations, Input_Matrix):
    Sign = np.zeros([len(Permutations[0, :]), len(Input_Matrix[0, :])]) #pre-allocation του μητρώου Sign το οποίο θα καταλήξει να
    #περιέχει τα signatures.
    """Kwdikas diaxwrismou omadwn"""
    #Η for αυτή δημιουργεί το signature ανά γραμμή για το κάθε αρχείο.
    for i in range(len(Input_Matrix[0, :])):
        t = []
        for j in range(len(Permutations[0, :])):
            temp = Permutations[:, j].copy()
            flag = False
            while (not flag):
                minimum = np.argmin(temp)
                if (int(Input_Matrix[minimum, i]) == 1):
                    flag = True
                else:
                    temp[minimum] = 99999

            t.append(temp[minimum])
        Sign[0:len(t), i] = t

    return Sign

"""Η συνάρτηση αυτή θα χρησιμοποιηθεί προαιρετικά για να επαληθεύσουμε το αποτέλεσμα της signature similarity και αν χρειαστεί,
να μετρήσουμε το error που θα προκύψει."""
def JaccardSim(smatrix):
    Jac = []
    #Η jaccard similarity παίρνει την ένωση του μητρώου και την τομή και εκτελεί την πράξη τομή/ένωση για να υπολογίσει το similarity.
    for k in range(len(smatrix[0, :])):
        for i in range(k + 1, len(smatrix[0, :])):
            intersection = 0
            union = 0
            for j in range(len(smatrix[:])):
                if (smatrix[j, k] == 1.0 or smatrix[j, i] == 1.0):
                    union += 1
                if (smatrix[j, k] == 1.0 and smatrix[j, i] == 1.0):
                    intersection += 1

            Jac.append(intersection / union)
    return Jac

"""H προσεγγιστική συνάρτηση υπολογισμού Similarity."""
def PermutationSim(signature):
    # Η signature similarity παίρνει την ένωση και την τομή του μητρώου Signature και εκτελεί την πράξη τομή/ένωση..
    Sim = []
    union = len(signature[:])
    for i in range(len(signature[0, :])):
        for j in range(i + 1, len(signature[0, :])):
            same = 0
            for k in range(len(signature[:])):
                # print('i,j,k = ', i, ' ', j, ' ', k)
                if (signature[k, i] == signature[k, j]):
                    same += 1
            Sim.append(same / union)

    return Sim