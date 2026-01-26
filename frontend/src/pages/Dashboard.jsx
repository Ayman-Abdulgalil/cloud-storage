import { useState } from 'react';
import { Upload, Folder, FileText, Settings, Search, MoreVertical, Home, Clock, Star, Trash2, Users, HardDrive, Download, Share2} from 'lucide-react';
import Logo from "../assets/logo.svg";

export default function Dashboard() {
    const [activeMenu, setActiveMenu] = useState(null);

    const files = [
        { id: 1, name: "Project Proposal.pdf", type: "PDF", size: "2.4 MB", modified: "2 hours ago", isFolder: false },
        { id: 2, name: "Budget 2024", type: "Folder", size: "—", modified: "Yesterday", isFolder: true },
        { id: 3, name: "Team Photos", type: "Folder", size: "—", modified: "3 days ago", isFolder: true },
        { id: 4, name: "presentation.pptx", type: "PPTX", size: "5.1 MB", modified: "1 week ago", isFolder: false },
        { id: 5, name: "data_analysis.xlsx", type: "XLSX", size: "892 KB", modified: "1 week ago", isFolder: false },
    ];

    const sidebarItems = [
        { icon: Home, text: "My Drive", active: true },
        { icon: Users, text: "Shared with me", active: false },
        { icon: Clock, text: "Recent", active: false },
        { icon: Star, text: "Starred", active: false },
        { icon: Trash2, text: "Trash", active: false },
    ];

    return (
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, display: "flex", height: "100vh", backgroundColor: "#f5f5f5", fontFamily: "system-ui, -apple-system, sans-serif" }}>
            {/* Sidebar */}
            <div style={{
                width: "260px",
                backgroundColor: "#ffffff",
                borderRight: "1px solid #e0e0e0",
                display: "flex",
                flexDirection: "column",
                padding: "16px"
            }}>
                {/* Logo */}
                <div style={{ marginBottom: "24px", display: "flex", alignItems: "center", gap: "1px" }}>
                    <img 
                        src={Logo} 
                        alt="Secure Drive logo" 
                        style={{ width: "45px", height: "45px" }} 
                    />
                    <span style={{ fontSize: "1.25rem", fontWeight: 700 }}>Secure Drive</span>
                </div>

                {/* Upload Button */}
                <button style={{
                    backgroundColor: "#4F46E5",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "12px 16px",
                    fontSize: "0.95rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    marginBottom: "16px",
                    width: "100%"
                }}
                onMouseOver={(e) => e.target.style.backgroundColor = "#4338CA"}
                onMouseOut={(e) => e.target.style.backgroundColor = "#4F46E5"}
                >
                    <Upload size={20} />
                    Upload
                </button>

                {/* Navigation Items */}
                <div style={{ flexGrow: 1 }}>
                    {sidebarItems.map((item, index) => (
                        <div
                            key={index}
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "12px",
                                padding: "12px 16px",
                                borderRadius: "8px",
                                cursor: "pointer",
                                marginBottom: "4px",
                                backgroundColor: item.active ? "#EEF2FF" : "transparent",
                                color: item.active ? "#4F46E5" : "#666"
                            }}
                            onMouseOver={(e) => {
                                if (!item.active) e.currentTarget.style.backgroundColor = "#f5f5f5";
                            }}
                            onMouseOut={(e) => {
                                if (!item.active) e.currentTarget.style.backgroundColor = "transparent";
                            }}
                        >
                            <item.icon size={20} />
                            <span style={{ fontSize: "0.95rem", fontWeight: item.active ? 600 : 400 }}>
                                {item.text}
                            </span>
                        </div>
                    ))}
                </div>

                {/* Storage Info */}
                <div style={{
                    marginTop: "auto",
                    padding: "16px",
                    backgroundColor: "#f9fafb",
                    borderRadius: "8px"
                }}>
                    <div style={{ display: "flex", alignItems: "center", marginBottom: "8px", gap: "8px" }}>
                        <HardDrive size={16} color="#666" />
                        <span style={{ fontSize: "0.875rem", color: "#666" }}>Storage</span>
                    </div>
                    <div style={{
                        width: "100%",
                        height: "6px",
                        backgroundColor: "#e0e0e0",
                        borderRadius: "4px",
                        marginBottom: "8px"
                    }}>
                        <div style={{
                            width: "45%",
                            height: "100%",
                            backgroundColor: "#4F46E5",
                            borderRadius: "4px"
                        }} />
                    </div>
                    <span style={{ fontSize: "0.75rem", color: "#999" }}>4.5 GB of 10 GB used</span>
                </div>
            </div>

            {/* Main Content */}
            <div style={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
                {/* Top Bar */}
                <div style={{
                    backgroundColor: "#ffffff",
                    borderBottom: "1px solid #e0e0e0",
                    padding: "16px 24px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between"
                }}>
                    {/* Search Bar */}
                    <div style={{
                        backgroundColor: "#f5f5f5",
                        borderRadius: "24px",
                        padding: "10px 20px",
                        display: "flex",
                        alignItems: "center",
                        width: "500px",
                        gap: "12px"
                    }}>
                        <Search size={20} color="#999" />
                        <input
                            type="text"
                            placeholder="Search in Drive"
                            style={{
                                border: "none",
                                backgroundColor: "transparent",
                                outline: "none",
                                width: "100%",
                                fontSize: "0.95rem"
                            }}
                        />
                    </div>

                    {/* Right Side */}
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <button style={{
                            width: "40px",
                            height: "40px",
                            borderRadius: "50%",
                            border: "none",
                            backgroundColor: "transparent",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center"
                        }}>
                            <Settings size={22} color="#666" />
                        </button>
                        <div style={{
                            width: "36px",
                            height: "36px",
                            borderRadius: "50%",
                            backgroundColor: "#4F46E5",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "white",
                            fontWeight: 600,
                            fontSize: "0.9rem"
                        }}>
                            U
                        </div>
                    </div>
                </div>

                {/* Content Area */}
                <div style={{ flexGrow: 1, overflow: "auto", padding: "32px" }}>
                    {/* Page Header */}
                    <div style={{ marginBottom: "24px" }}>
                        <h1 style={{ fontSize: "1.5rem", fontWeight: 600, margin: "0 0 4px 0" }}>My Drive</h1>
                        <p style={{ fontSize: "0.875rem", color: "#666", margin: 0 }}>{files.length} items</p>
                    </div>

                    {/* Quick Access */}
                    <div style={{ marginBottom: "32px" }}>
                        <h2 style={{ fontSize: "0.75rem", fontWeight: 600, color: "#999", margin: "0 0 16px 0", letterSpacing: "0.5px" }}>
                            QUICK ACCESS
                        </h2>
                        <div style={{ display: "flex", gap: "16px" }}>
                            {files.slice(0, 3).map((file) => (
                                <div
                                    key={file.id}
                                    style={{
                                        padding: "16px",
                                        width: "200px",
                                        backgroundColor: "white",
                                        borderRadius: "8px",
                                        cursor: "pointer",
                                        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                                        transition: "box-shadow 0.2s"
                                    }}
                                    onMouseOver={(e) => e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)"}
                                    onMouseOut={(e) => e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.1)"}
                                >
                                    <div style={{ display: "flex", alignItems: "center", marginBottom: "8px" }}>
                                        {file.isFolder ? 
                                            <Folder size={24} color="#FFA726" /> : 
                                            <FileText size={24} color="#666" />
                                        }
                                        <button style={{
                                            marginLeft: "auto",
                                            border: "none",
                                            backgroundColor: "transparent",
                                            cursor: "pointer",
                                            padding: "4px"
                                        }}>
                                            <MoreVertical size={16} color="#999" />
                                        </button>
                                    </div>
                                    <p style={{
                                        fontSize: "0.875rem",
                                        fontWeight: 500,
                                        margin: "0 0 4px 0",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                        whiteSpace: "nowrap"
                                    }}>
                                        {file.name}
                                    </p>
                                    <p style={{ fontSize: "0.75rem", color: "#999", margin: 0 }}>
                                        {file.modified}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Files List */}
                    <div>
                        <h2 style={{ fontSize: "0.75rem", fontWeight: 600, color: "#999", margin: "0 0 16px 0", letterSpacing: "0.5px" }}>
                            FILES
                        </h2>
                        <div style={{ backgroundColor: "white", borderRadius: "8px", overflow: "hidden" }}>
                            {/* Table Header */}
                            <div style={{
                                display: "grid",
                                gridTemplateColumns: "2fr 1fr 1fr 100px",
                                padding: "16px",
                                backgroundColor: "#fafafa",
                                borderBottom: "1px solid #e0e0e0"
                            }}>
                                <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#999" }}>NAME</span>
                                <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#999" }}>TYPE</span>
                                <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#999" }}>MODIFIED</span>
                                <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#999" }}>SIZE</span>
                            </div>

                            {/* Table Rows */}
                            {files.map((file, index) => (
                                <div
                                    key={file.id}
                                    style={{
                                        display: "grid",
                                        gridTemplateColumns: "2fr 1fr 1fr 100px",
                                        padding: "16px",
                                        borderBottom: index < files.length - 1 ? "1px solid #f0f0f0" : "none",
                                        alignItems: "center",
                                        cursor: "pointer"
                                    }}
                                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#fafafa"}
                                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                                >
                                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                                        {file.isFolder ? 
                                            <Folder size={20} color="#FFA726" /> : 
                                            <FileText size={20} color="#666" />
                                        }
                                        <span style={{ fontSize: "0.875rem", fontWeight: 500 }}>{file.name}</span>
                                    </div>
                                    <span style={{ fontSize: "0.875rem", color: "#666" }}>{file.type}</span>
                                    <span style={{ fontSize: "0.875rem", color: "#666" }}>{file.modified}</span>
                                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                                        <span style={{ fontSize: "0.875rem", color: "#666" }}>{file.size}</span>
                                        <button 
                                            style={{
                                                border: "none",
                                                backgroundColor: "transparent",
                                                cursor: "pointer",
                                                padding: "4px",
                                                position: "relative"
                                            }}
                                            onClick={() => setActiveMenu(activeMenu === file.id ? null : file.id)}
                                        >
                                            <MoreVertical size={16} color="#999" />
                                            {activeMenu === file.id && (
                                                <div style={{
                                                    position: "absolute",
                                                    right: 0,
                                                    top: "100%",
                                                    backgroundColor: "white",
                                                    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                                                    borderRadius: "8px",
                                                    padding: "8px 0",
                                                    minWidth: "160px",
                                                    zIndex: 10
                                                }}>
                                                    <div style={{
                                                        padding: "8px 16px",
                                                        cursor: "pointer",
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: "12px",
                                                        fontSize: "0.875rem"
                                                    }}
                                                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#f5f5f5"}
                                                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                                                    >
                                                        <Download size={16} />
                                                        Download
                                                    </div>
                                                    <div style={{
                                                        padding: "8px 16px",
                                                        cursor: "pointer",
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: "12px",
                                                        fontSize: "0.875rem"
                                                    }}
                                                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#f5f5f5"}
                                                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                                                    >
                                                        <Share2 size={16} />
                                                        Share
                                                    </div>
                                                    <div style={{
                                                        padding: "8px 16px",
                                                        cursor: "pointer",
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: "12px",
                                                        fontSize: "0.875rem"
                                                    }}
                                                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#f5f5f5"}
                                                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                                                    >
                                                        <Star size={16} />
                                                        Add to Starred
                                                    </div>
                                                    <div style={{ height: "1px", backgroundColor: "#e0e0e0", margin: "4px 0" }} />
                                                    <div style={{
                                                        padding: "8px 16px",
                                                        cursor: "pointer",
                                                        display: "flex",
                                                        alignItems: "center",
                                                        gap: "12px",
                                                        fontSize: "0.875rem",
                                                        color: "#dc2626"
                                                    }}
                                                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#fee2e2"}
                                                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                                                    >
                                                        <Trash2 size={16} />
                                                        Delete
                                                    </div>
                                                </div>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}