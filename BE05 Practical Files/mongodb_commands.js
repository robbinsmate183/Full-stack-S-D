// COM661 - Full Stack Strategies and Development
// BE05 - MongoDB Practical


// ========================================
// 1. CREATE DATABASE AND COLLECTION
// ========================================

// Run this first in mongosh:
// use first

db.createCollection("fullStack");


// ========================================
// 2. INSERT DOCUMENTS
// ========================================

db.fullStack.insertMany([
    { name: "MongoDB", role: "Database" },
    { name: "Flask", role: "Web application framework" },
    { name: "Angular", role: "Front-end framework" },
    { name: "Python", role: "Back-end language" }
]);

db.fullStack.find();


// ========================================
// 3. CREATE SECOND COLLECTION
// ========================================

db.createCollection("games");

db.games.insertMany([
    { name: "Minecraft", genre: "Survival", rating: 5 },
    { name: "Rocket League", genre: "Sports", rating: 4 },
    { name: "CS2", genre: "Shooter", rating: 5 }
]);

db.games.find();


// ========================================
// 4. SEARCHING DOCUMENTS
// ========================================

db.fullStack.find({ name: "Flask" });

db.fullStack.find({
    name: "MongoDB",
    role: "Database"
});

db.games.find({ rating: 5 });


// ========================================
// 5. PROJECTION
// ========================================

db.fullStack.find(
    { name: "MongoDB" },
    { role: 1, _id: 0 }
);

db.fullStack.find(
    {},
    { name: 1, _id: 0 }
);


// ========================================
// 6. SORTING
// ========================================

// Ascending
db.fullStack.find().sort({ name: 1 });

// Descending
db.fullStack.find().sort({ name: -1 });

// Sort games
db.games.find().sort({ name: 1 });


// ========================================
// 7. UPDATING DOCUMENTS
// ========================================

// Update one business technology
db.fullStack.updateOne(
    { name: "MongoDB" },
    { $set: { name: "Mongo" } }
);

// Update all documents
db.fullStack.updateMany(
    {},
    { $set: { module: "COM661" } }
);

// Update a game
db.games.updateOne(
    { name: "Minecraft" },
    { $set: { rating: 4 } }
);

// Verify changes
db.fullStack.find();
db.games.find();


// ========================================
// 8. DELETING DOCUMENTS
// ========================================

// Delete Angular
db.fullStack.deleteOne({ name: "Angular" });

// Delete CS2
db.games.deleteOne({ name: "CS2" });

// Verify
db.fullStack.find();
db.games.find();


// ========================================
// 9. DELETE COLLECTION CONTENTS
// ========================================

db.games.deleteMany({});
db.fullStack.deleteMany({});


// ========================================
// 10. DROP COLLECTIONS
// ========================================

db.games.drop();
db.fullStack.drop();


// ========================================
// 11. RECREATE ORIGINAL COLLECTION
// ========================================

db.createCollection("fullStack");

db.fullStack.insertMany([
    { name: "MongoDB", role: "Database" },
    { name: "Flask", role: "Web application framework" },
    { name: "Angular", role: "Front-end framework" },
    { name: "Python", role: "Back-end language" }
]);

db.fullStack.find();


// ========================================
// 12. EXPORT AND IMPORT DATA
// ========================================

// The following commands are run in
// PowerShell, NOT inside mongosh.
//
// mongodump --db first
//
// mongorestore --nsFrom="first.*" --nsTo="second.*" dump
//
// mongoexport --db first --collection fullStack --out data.json --jsonArray --pretty
//
// mongoimport --db third --collection fullStack --jsonArray --file data.json


// ========================================
// 13. VERIFY DATABASES
// ========================================

// Run separately inside mongosh:
//
// use second
// db.fullStack.find()
//
// use third
// db.fullStack.find()
//
// show dbs