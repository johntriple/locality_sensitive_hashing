from bitarray import bitarray
import mmh3
import numpy as np


def ArrayInit(Input_num,False_Positive_Posibility): #Αρχικοποιήση του bit array με γνωστό πλήθος εισόδου και πιθανότητα εμφάνισης false positive
    m = int(- np.log(False_Positive_Posibility) * Input_num  / (np.log(2)) ** 2) #υπολογισμός του βέλτιστου μεγέθους του bit array
    ba = bitarray(m) #αρχικοποιηση του μεγέθους του bit array μεγέθους m
    ba.setall(False) #Αρχικοποιήση των τιμών του bit_array με μηδενικά
    return ba

def Hash(Input_num,BitArraySize):
    k = int(np.log(2) * BitArraySize / Input_num) #Εύρεση βέλτιστου αριθμού hash functions
    return k

def Add(Bit_Array,NumOfHashes,item): #Προσθήκη ενός στοιχείου στο φίλτρο
    #kati = [] #Προσωρινη λίστα που θα περιέχει τα αποτελέσματα των hash functions
    for i in range(NumOfHashes):
        katis = mmh3.hash(item, i) % len(Bit_Array) #Χρήση mmh3 βιβλιοθήκης για hashing του στοιχείου i στο bit array
        #kati.append(katis)
        Bit_Array[katis] = True #Όπου πέσει το αποτέλεσμα του hash function άλλαξε την τιμή σε εκείνη τη θέση σε '1'
    return Bit_Array

def Check(Bit_Array,NumOfHashes,item): #Έλεγχος ύπαρξης στοιχείου εντός του φίλτρου
    for i in range(NumOfHashes):
        katis = mmh3.hash(item, i) % len(Bit_Array) #Χρήση mmh3 βιβλιοθήκης για hashing του στοιχείου i στο bit array
        if (not Bit_Array[katis]): #Αν όλα τα στοιχεία bit array με indexes τα αποτελέσματα των hash function είναι 1 τότε επέστρεψε TRUE αλλιώς FALSE
            return False
    return True #To true εδω είναι φαινομενικό. Δηλώνει ότι ίσως το στοιχείο να βρίσκεται στο φίλτρο.