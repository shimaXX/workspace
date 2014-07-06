package Aggregate;

import java.util.*;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.FileWriter;

import org.omg.CORBA.SystemException;


public class Main {
	public static void main(String[] args){
		loadData ld = new loadData("test.txt");
		ld.getData();
	}
}
