package main

import (
	"flag"
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

var (
	address string
	port string
	ip string
	publicDir string
)

func logRequest(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log.Printf("%s %s %s", r.Method, r.URL.Path, r.Proto)
		next.ServeHTTP(w, r)
	})
}

// output html
func outputHTML(w http.ResponseWriter, filename string, data interface{}) {
	t, err := template.ParseFiles(filename)
	if err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
	if err := t.Execute(w, data); err != nil {
		http.Error(w, err.Error(), 500)
		return
	}
 }

func getRoot(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, "/files", http.StatusFound)
	//outputHTML(w, "index.html", nil)
}

func serveFile(w http.ResponseWriter, r *http.Request) {
	filePath := strings.TrimPrefix(r.URL.Path, "/files/")
	fullPath := filepath.Join(publicDir, filePath)

	info, err := os.Stat(fullPath)
	if err != nil {
		log.Printf("Error: file not found: %s", fullPath)
		http.Error(w, "File not found", http.StatusNotFound)
		return
	}

	if info.IsDir() {
		files, err := os.ReadDir(fullPath)
		if err != nil {
			log.Println("Error reading directory:", fullPath)
			http.Error(w, "Error reading directory", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		io.WriteString(w, "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n")
		io.WriteString(w, "<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
		io.WriteString(w, fmt.Sprintf("<title>Directory listing for %s/</title>\n</head>\n<body>\n", info.Name()))

		io.WriteString(w, fmt.Sprintf("<h1>%s</h1>\n", r.URL.Path))
		io.WriteString(w, "<hr>\n<ul>\n")
		for _, file := range files {
			if file.IsDir() {
				io.WriteString(w, fmt.Sprintf("<li><a href=\"%s/\">%s/</a></li>\n", filepath.Join(r.URL.Path, file.Name()), file.Name()))
			} else {
				//fullFilePath := filepath.Join(fullPath, file.Name())
				// fileInfo, err := os.Stat(fullFilePath)
				// if err != nil {
				// 	log.Printf("Error: could not get file size for %s: %v", fullFilePath, err)
				// 	continue
				// }
				//fileSizeKB := fileInfo.Size() / 1024
				// io.WriteString(w, fmt.Sprintf("<li><a href=\"%s\">%s (%d KB)</a></li>\n", filepath.Join(r.URL.Path, file.Name()), file.Name(), fileSizeKB))
				io.WriteString(w, fmt.Sprintf("<li><a href=\"%s\">%s</a></li>\n", filepath.Join(r.URL.Path, file.Name()), file.Name()))
			}
		}
	} else {
		file, err := os.Open(fullPath)
		if err != nil {
			log.Printf("Error: could not open file: %s", fullPath)
			http.Error(w, "Error opening file", http.StatusInternalServerError)
			return
		}
		defer file.Close()

		http.ServeContent(w, r, fullPath, info.ModTime(), file)
	}
}

func serveAudio(w http.ResponseWriter, r *http.Request) {
	audioFilePath := ("شيلة كلنا سلمان كلنا محمد اداء شبل الدواسر 2019.wav")
	file, err := os.Open(audioFilePath)
	if err != nil {
		log.Printf("Error: could not open audio file to serve: %s", audioFilePath)
		http.Error(w, "Audio file not found", http.StatusNotFound)
		return
	}
	defer file.Close()

	w.Header().Set("Content-Type", "audio/mpeg")
	http.ServeContent(w, r, audioFilePath, time.Now(), file)
}

func serveVideo(w http.ResponseWriter, r *http.Request) {
	videoFilePath := ("oldman.mp4")
	file, err :=os.Open(videoFilePath)
	if err != nil {
		log.Printf("Error: could not open audio file to serve: %s", videoFilePath)
		http.Error(w, "Video file not found", http.StatusNotFound)
	}
	defer file.Close()
	w.Header().Set("Content-Type", "video/mp4")
	http.ServeContent(w, r, videoFilePath, time.Now(), file)
}


func main() {
	// check for arguments
	addressArg := flag.String("address", "not_provided", "The address on which to bind the server")
	portArg := flag.String("port", "not_provided", "The port on which to bind the server")
	directoryArg := flag.String("dir", ".", "The directory that the server broadcasts")
	flag.Parse()

	if flag.NFlag() == 0 {
		flag.Usage()
		os.Exit(0)
	}
	
	if *addressArg != "not_provided" {
		address = *addressArg
	}else {
		fmt.Println("Must provide server address as argument.")
		os.Exit(0)
	}

	if *portArg != "not_provided" {
		port = *portArg
	}else {
		fmt.Println("Must provide server port as argument.")
		os.Exit(0)
	}

	publicDir = *directoryArg

	ip = fmt.Sprintf("%s:%s", *addressArg, *portArg)

	mux := http.NewServeMux()
	mux.HandleFunc("/", getRoot)
	mux.HandleFunc("/files/", serveFile)
	mux.HandleFunc("/audio/", serveAudio)
	mux.HandleFunc("/video/", serveVideo)

	loggedMux := logRequest(mux)

	fmt.Printf("Starting server on http://%s...\n", ip)
	if err := http.ListenAndServe(ip, loggedMux); err != nil {
		log.Fatal("Error starting server: ", err)
	}
}
// https://media.discordapp.net/attachments/864353121474707468/1022687072022175824/Sequence_01.gif?ex=6794440e&is=6792f28e&hm=4956aa020a29cf5561d62e6be4bc20ad1d276adff535aa723ab65de9a5f6dd65&