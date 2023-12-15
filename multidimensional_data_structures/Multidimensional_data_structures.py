import Shingles as sh
import time
import math


filesNo = int(input("Gia posa arxeia 8es na to tre3w: ")) #Ορισμός του πλήθους αρχείων με είσοδο από τον χρήστη

DocTest = [] #Λίστα που θα περιέχει τα αρχεία που θα ελέγξουμε
DocNames = [] #Λίστα που θα περιέχει τα ονόματα των αρχείων που εισάγαμε
parsed_texts = [] #Λιστα που θα περιέχει την pre-processed έκδοση των αρχείων
shingles = [] #Λίστα που θα περιέχει το διάνυσμα shingles για κάθε αρχείων

for c in range(filesNo): #Έλεγχος για ορθότητα εισαγωγής αρχείων και καταγραφή των ορθών στις αντίστοιχες λίστες.

    DocTest.append('NULL')
    end = False

    while (not end): #Όσο ο χρήστης δίνει λανθασμένη είσοδο, ξαναζήτα είσοδο.
        try:
            checked = True
            kati = input("Give me the name of the text file or its directory path\n")
            text1 = open(kati)
            testing = [text1.read()]

            DocTest[c] = kati

            for k in range(len(DocTest) - 1):
                if (DocTest[k] == kati): checked = False
            if (checked == True):
                DocNames.append(DocTest[c])
                end = True

            else:
                print('A Document with that name was already given. Please try again!\n')

        except OSError as error:
            print('Error: File does not exist. Please try again!\n')
    parsed_texts.append(sh.Parse(DocNames[c])) #Τοποθέτηση στην λίστα των pre-processed αρχείων
    shingles.append(sh.Shingles(parsed_texts[c],3)) #Τοποθέτηση στη λίστα των shingles που προκύπτουν για το κάθε αρχείο.



start = time.time() #Εκκίνηση timer
candidates = [] #Αρχικοποιήση λίστας candidates που θα αποθηκεύει τα υποψήφια αρχεία προς σύγκριση.
#Σύγκρινε όλους τους πιθανούς συνδυασμούς αρχείων χωρίς επανάληψη
for i in range(len(DocNames)):
    for j in range(i+1,len(DocNames)):
        #if (i == j): continue
        #print("We are talking about files: {0} and {1}".format(DocNames[i],DocNames[j]))
        matrix = sh.SMatrix(shingles[i],shingles[j]) #Αποθήκευση του παραγόμενου μητρώου για ένα pair
        #jac = sh.JaccardSim(matrix)
        #l = sh.Permutations(matrix,100)
        #l = sh.Signature(l,matrix)
        #l = sh.PermutationSim(l)
        #print(jac)

        n = len(matrix[:]) #Αποθήκευση του πλήθους των γραμμών του μητρώου

        #Χρήση της μεθόδου του μέγιστου κοινού διαιρέτη για να υπολογίσουμε έναν καλό συνδυασμό bands και rows για την υλοποιήση του LSH.
        GCD = math.gcd(n, 2)
        bands = int(n / GCD)
        rows = int(n / bands)
        for prime_check in range(4):
            for g in range(2, 11):
                if (rows > 10): break
                if (GCD == 1):
                    GCD = math.gcd(bands, g)
                    #print("For i {0} we have GCD = {1}".format(g, GCD))

                else:
                    while (GCD != 1 and rows < 10):
                        #print("mpainw edw gia to i {}".format(g - 1))
                        GCD = math.gcd(bands, g - 1)
                        temp = bands
                        bands = int(temp / GCD)
                        rows = int(n / bands)
                        if (rows > 30):
                            bands = temp
                            rows = int(n / bands)
                            break
            #print("bands = {0}, rows = {1}, n = {2}, bands * rows = {3}".format(bands, rows, n, bands*rows))
            if (bands * rows != n):
                n += 1
                band = n
            if (rows < 10 and prime_check > 1 and prime_check < 3):
                bands += 1
                n += rows
            elif(rows < 10 and prime_check == 3): break
                #rows = int(n/bands)
            if (rows > 10): break

        #Σε περίπτωση που το n είναι πρώτος αριθμός το κάνουμε handle, προβλέποντας ότι θα προκύψει κάποιο error το οποίο και διορθώνουμε στην πορεία για να αποφύγουμε το out of bounds exception ή την απώλεια πληροφορίας.
        #Δεν υπάρχει περίπτωση για εμφάνιση false positive με αυτή τη διόρθωση λόγο του τρόπου δημιουργίας του matrix που βεβαιώνει πως δεν θα έχουμε όμοια στοιχεία στις τελευταίες θέσεις του μητρώου.
        error = 0
        for k in range(bands):
            same = 0
            if (k == (bands - 1)):
                error = bands*rows - len(matrix)
                rows = rows - error
            for p in range(rows):
                if (matrix[k*(rows + error) + p,0] == matrix[k*rows + p,1]):
                    same += 1
            if(same == rows):
                candidates.append([i,j]) #Αν όλα τα στοιχεία σε ένα band είναι όμοια τοποθέτησε το pair στην λίστα candidates.
                #print(candidates)
                break

print(candidates) #Εμφάνιση στην οθόνη της λίστας candidates



for i in range(len(candidates)): #Πλέον βρίσκουμε την ομοιότητα των pairs που θεωρήσαμε ως candidates από την παραπάνω διαδικασία.
    m = sh.SMatrix(shingles[candidates[i][0]], shingles[candidates[i][1]])
    jac = sh.JaccardSim(m) #Εύρεση Jaccard Similarity του pair για σύγκριση με την προσεγγιστική μέθοδο του minhash.
    print("We are talking about files {0} and {1}".format(DocNames[candidates[i][0]],DocNames[candidates[i][1]]))
    print(jac)
    sim = sh.Permutations(m,10) #Δημιουργία 10 permutation vectors για το μητρώο m
    sim = sh.Signature(sim,m) #Δημιουργία του Signature matrix
    sim = sh.PermutationSim(sim) #Υπολογισμός της προσεγγιστικής ομοιότητας με τη μέθοδο του minhash
    print(sim)

end = time.time() #Λήξη του timer
print("Time elapsed is {} seconds!".format(end - start)) #Εμφάνιση στην οθόνη του συνολικού χρόνου εκτέλεσης της όλης διαδικασίας.