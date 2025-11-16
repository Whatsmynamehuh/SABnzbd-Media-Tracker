#!/bin/bash
# Reset poster_attempted flags to retry failed poster lookups with new matching algorithm

echo "Resetting poster flags to retry with improved matching algorithm..."
curl -X POST http://localhost:3001/api/admin/reset-poster-flags
echo ""
echo "Done! Poster fetching will now retry all failed items with the new matching algorithm."
