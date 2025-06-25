SELECT data_quality_flags, COUNT(*) 
FROM transactions 
GROUP BY data_quality_flags
ORDER BY COUNT(*) DESC;
