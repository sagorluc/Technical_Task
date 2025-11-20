SELECT COUNT(*) FROM emp_talbe
WHERE FirstName LIKE "%e%" 
AND CHAR_LENGTH(LastName) > 5;