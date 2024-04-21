sig Person {
    name: String,
    age: Int
}

sig Department {
    name: String
}


fact {
    WorksIn in Person -> Department
}