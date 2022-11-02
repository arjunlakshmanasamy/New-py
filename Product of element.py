'''Write a program that returns the product of all elements present in the list.
Constraints:

1 <= |A| <= 100
1 <= A <= 100
Note: It is guaranteed that the resultant product will be <= 1015
Input Format:

An integer array A as the function argument.
Output Format:

Product of elements in integer format
Sample Input:

A = [7, 9, 2, 51]
Sample Output:

6426
Sample explanation:

The product of all the elements is 7 * 9 * 2 * 51 = 6426 is returned.'''

def product(lst):
    ''' input:lst-List of elements in integer format
         output:Return the product as result.'''
    
    result = 1
    # YOUR CODE GOES HERE
    for i in lst:
      result*=i
        
    
    return result